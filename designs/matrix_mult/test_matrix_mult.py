"""cocotb tests for matrix_mult (3x3 matrix multiplier, flat ports).

Mirrors the UVM checks: reference model in Python, directed corner cases,
random full-range matrices, back-to-back starts and reset in the middle.
"""
import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge, RisingEdge, Timer

A_W = 8     # element width of A and B
C_W = 20    # element width of C
MAX_C = 3 * 255 * 255


def pack(m, width=A_W):
    """3x3 list-of-lists -> flat integer, element (i, j) at offset (i*3+j)*width."""
    value = 0
    for i in range(3):
        for j in range(3):
            value |= m[i][j] << ((i * 3 + j) * width)
    return value


def unpack(value, width=C_W):
    """Flat integer -> 3x3 list-of-lists."""
    mask = (1 << width) - 1
    return [[(value >> ((i * 3 + j) * width)) & mask for j in range(3)] for i in range(3)]


def matmul(a, b):
    """Reference model: C = A x B."""
    return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def rand_matrix(corner_bias=True):
    """Random 8-bit matrix; corner values 0 and 255 are over-represented."""
    pool = [0, 1, 255, 254, 128]
    return [[random.choice(pool) if (corner_bias and random.random() < 0.4)
             else random.randint(0, 255) for _ in range(3)] for _ in range(3)]


async def reset(dut):
    """Start the clock (once per test) and apply reset."""
    cocotb.start_soon(Clock(dut.clk, 10, "ns").start())
    dut.rst_n.value = 0
    dut.start.value = 0
    dut.a_flat.value = 0
    dut.b_flat.value = 0
    await ClockCycles(dut.clk, 3)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)


async def run_one(dut, a, b):
    """One transaction: single-cycle start, check result, done pulse and hold."""
    await FallingEdge(dut.clk)
    dut.a_flat.value = pack(a)
    dut.b_flat.value = pack(b)
    dut.start.value = 1
    await FallingEdge(dut.clk)              # the rising edge in between sampled start = 1
    dut.start.value = 0
    dut.a_flat.value = pack(rand_matrix())  # inputs change after the start edge
    dut.b_flat.value = pack(rand_matrix())  # ...the result must not depend on them
    assert int(dut.done.value) == 1, "done must be high one cycle after start"
    got = unpack(int(dut.c_flat.value))
    expected = matmul(a, b)
    assert got == expected, f"A={a}\nB={b}\ngot={got}\nexpected={expected}"
    await FallingEdge(dut.clk)
    assert int(dut.done.value) == 0, "done must be a one-cycle pulse"
    assert unpack(int(dut.c_flat.value)) == expected, "c must hold its value when idle"


@cocotb.test()
async def test_reset_values(dut):
    """After reset: done = 0 and every C element is 0."""
    await reset(dut)
    assert int(dut.done.value) == 0
    assert int(dut.c_flat.value) == 0


@cocotb.test()
async def test_directed(dut):
    """Zero, identity, all-255, a hand-checked example, and idle hold."""
    await reset(dut)
    zero = [[0] * 3 for _ in range(3)]
    ident = [[1 if i == j else 0 for j in range(3)] for i in range(3)]
    full = [[255] * 3 for _ in range(3)]
    a = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    b = [[9, 8, 7], [6, 5, 4], [3, 2, 1]]

    await run_one(dut, a, zero)       # A x 0 = 0
    await run_one(dut, zero, b)       # 0 x B = 0
    await run_one(dut, a, ident)      # A x I = A
    await run_one(dut, ident, b)      # I x B = B
    await run_one(dut, full, full)    # maximum: every element = 3*255*255
    assert unpack(int(dut.c_flat.value)) == [[MAX_C] * 3 for _ in range(3)]
    assert matmul(a, b) == [[30, 24, 18], [84, 69, 54], [138, 114, 90]]
    await run_one(dut, a, b)
    for _ in range(5):                # idle: value held, done stays low
        await FallingEdge(dut.clk)
        assert int(dut.done.value) == 0
        assert unpack(int(dut.c_flat.value)) == matmul(a, b)


@cocotb.test()
async def test_random(dut):
    """200 random full-range matrices with corner values over-represented."""
    random.seed(1234)
    await reset(dut)
    for _ in range(200):
        await run_one(dut, rand_matrix(), rand_matrix())


@cocotb.test()
async def test_back_to_back(dut):
    """start held high: a new result every cycle, done stays high."""
    random.seed(99)
    await reset(dut)
    sent = []
    await FallingEdge(dut.clk)
    for _ in range(6):
        a, b = rand_matrix(), rand_matrix()
        dut.a_flat.value = pack(a)
        dut.b_flat.value = pack(b)
        dut.start.value = 1
        sent.append((a, b))
        await FallingEdge(dut.clk)
        assert int(dut.done.value) == 1
        assert unpack(int(dut.c_flat.value)) == matmul(*sent[-1])
    dut.start.value = 0
    await FallingEdge(dut.clk)
    assert int(dut.done.value) == 0


@cocotb.test()
async def test_reset_mid_operation(dut):
    """Asynchronous reset right after a start edge clears done and C."""
    await reset(dut)
    full = [[255] * 3 for _ in range(3)]
    await FallingEdge(dut.clk)
    dut.a_flat.value = pack(full)
    dut.b_flat.value = pack(full)
    dut.start.value = 1
    await RisingEdge(dut.clk)               # DUT samples start here
    await Timer(1, "ns")
    dut.start.value = 0
    dut.rst_n.value = 0                     # asynchronous reset, mid-operation
    await Timer(1, "ns")
    assert int(dut.done.value) == 0
    assert int(dut.c_flat.value) == 0
    await ClockCycles(dut.clk, 2)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)
    assert int(dut.done.value) == 0
    assert int(dut.c_flat.value) == 0

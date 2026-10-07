import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer, ReadOnly


async def reset_dut(dut):
    dut.rst_n.value = 0
    dut.ready.value = 0
    dut.valid.value = 0
    await Timer(2, unit="ns")
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)
    await ReadOnly()


async def cycle(dut, ready=0, valid=0):
    # Leave the previous ReadOnly phase before driving the next cycle.
    await Timer(1, unit="ns")
    dut.ready.value = ready
    dut.valid.value = valid
    await RisingEdge(dut.clk)
    await ReadOnly()


def outputs(dut):
    return (
        int(dut.handshake_ok.value),
        int(dut.error_early.value),
        int(dut.error_late.value),
        int(dut.error_missing.value),
    )


@cocotb.test()
async def test_early_valid_is_rejected(dut):
    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())
    await reset_dut(dut)
    await cycle(dut, ready=1, valid=1)
    assert outputs(dut) == (0, 1, 0, 0)


@cocotb.test()
async def test_valid_exactly_one_cycle_late_is_accepted(dut):
    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())
    await reset_dut(dut)
    await cycle(dut, ready=1, valid=0)
    assert outputs(dut) == (0, 0, 0, 0)
    await cycle(dut, ready=0, valid=1)
    assert outputs(dut) == (1, 0, 0, 0)


@cocotb.test()
async def test_valid_after_deadline_is_late(dut):
    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())
    await reset_dut(dut)
    await cycle(dut, ready=1, valid=0)
    await cycle(dut, ready=0, valid=0)
    await cycle(dut, ready=0, valid=1)
    assert outputs(dut) == (0, 0, 1, 0)


@cocotb.test()
async def test_missing_valid_raises_missing_error(dut):
    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())
    await reset_dut(dut)
    await cycle(dut, ready=1, valid=0)
    for _ in range(5):
        await cycle(dut, ready=0, valid=0)
    assert outputs(dut) == (0, 0, 0, 1)

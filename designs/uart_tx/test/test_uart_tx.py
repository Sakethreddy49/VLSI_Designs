import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles

CLKS_PER_BIT = 8  # must match the -P override in the Makefile

@cocotb.test()
async def send_bytes(dut):
    cocotb.start_soon(Clock(dut.clk, 10, "ns").start())
    dut.rst_n.value = 0
    dut.tx_start.value = 0
    dut.tx_data.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)

    for byte in [0x55, 0xA3, 0x00, 0xFF]:
        dut.tx_data.value = byte
        dut.tx_start.value = 1
        await RisingEdge(dut.clk)
        dut.tx_start.value = 0

        while int(dut.tx.value) == 1:          # wait for the start bit
            await RisingEdge(dut.clk)
        await ClockCycles(dut.clk, CLKS_PER_BIT // 2)
        assert int(dut.tx.value) == 0, "start bit should be 0"

        received = 0
        for i in range(8):                     # LSB first
            await ClockCycles(dut.clk, CLKS_PER_BIT)
            received |= int(dut.tx.value) << i

        await ClockCycles(dut.clk, CLKS_PER_BIT)
        assert int(dut.tx.value) == 1, "stop bit should be 1"
        assert received == byte, f"sent {byte:#04x}, got {received:#04x}"

        while int(dut.busy.value):
            await RisingEdge(dut.clk)
        dut._log.info(f"byte {byte:#04x} OK")
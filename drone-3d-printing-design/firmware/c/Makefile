# Makefile for drone_firmware.c
# Targets: sim (default), arduino, stm32f1, stm32f4

CC       = gcc
AVRGCC   = avr-gcc
ARMGCC   = arm-none-eabi-gcc
OBJCOPY  = arm-none-eabi-objcopy
AVROBJCOPY = avr-objcopy

SRC = drone_firmware.c
CFLAGS_COMMON = -Wall -Wextra -O2 -lm

.PHONY: all sim arduino stm32f1 stm32f4 clean

all: sim

# ── Simulation (native) ────────────────────────────────────────────────────
sim: $(SRC)
	$(CC) -std=c11 $(CFLAGS_COMMON) -o drone_sim $(SRC)
	@echo "Built: drone_sim  (run with ./drone_sim)"

# ── Arduino Nano / Uno (ATmega328P) ────────────────────────────────────────
arduino: $(SRC)
	$(AVRGCC) -mmcu=atmega328p -DF_CPU=16000000UL -std=c11 -Os \
	    -o drone_arduino.elf $(SRC) -lm
	$(AVROBJCOPY) -O ihex drone_arduino.elf drone_arduino.hex
	@echo "Built: drone_arduino.hex"

# ── STM32F103 Blue Pill (Cortex-M3) ────────────────────────────────────────
stm32f1: $(SRC)
	$(ARMGCC) -mcpu=cortex-m3 -mthumb -std=c11 -O2 -nostartfiles \
	    -T /dev/null \
	    -o drone_stm32f1.elf $(SRC) -lm -lgcc
	@echo "Built: drone_stm32f1.elf  (flash with OpenOCD)"

# ── STM32F405 (Cortex-M4F) ────────────────────────────────────────────────
stm32f4: $(SRC)
	$(ARMGCC) -mcpu=cortex-m4 -mthumb -mfpu=fpv4-sp-d16 -mfloat-abi=hard \
	    -std=c11 -O2 -nostartfiles \
	    -T /dev/null \
	    -o drone_stm32f4.elf $(SRC) -lm -lgcc
	@echo "Built: drone_stm32f4.elf  (flash with OpenOCD)"

clean:
	rm -f drone_sim drone_*.elf drone_*.hex


/*
 * Copyright 2021-2024 NXP
 * All rights reserved.
 * (Macronix Flash Configuration for 16MB Flash)
 * SPDX-License-Identifier: BSD-3-Clause
 */
#include "flash_config.h"

/* Component ID definition, used by tools. */
#ifndef FSL_COMPONENT_ID
#define FSL_COMPONENT_ID "platform.drivers.flash_config"
#endif

/*******************************************************************************
 * Code
 ******************************************************************************/
#if defined(BOOT_HEADER_ENABLE) && (BOOT_HEADER_ENABLE == 1)
#if defined(__ARMCC_VERSION) || defined(__GNUC__)
__attribute__((section(".flash_conf"), used))
#elif defined(__ICCARM__)
#pragma location = ".flash_conf"
#endif
const fc_flexspi_nor_config_t flexspi_config = {
    .memConfig =
        {
            .tag                 = FC_BLOCK_TAG,
            .version             = FC_BLOCK_VERSION,
            .readSampleClkSrc    = 1,
            .csHoldTime          = 3,
            .csSetupTime         = 3,
            .deviceModeCfgEnable = 1,
            .deviceModeSeq       = {.seqNum = 1, .seqId = 2},
            /* 16MB/128Mbits MX25L12845G
             * deviceModeArg = 0xC740 (Write order: 0x40(SR) first, then 0xC7(CR))
             *
             * Low Byte 0x40 = Status Register (SR) - Written first
             *   Bit 7 (SRWD)       = 0: Hardware write protection disabled
             *   Bit 6 (QE)         = 1: ★Enable Quad mode (Critical! Must be set)
             *   Bit 5-2 (BP[3:0])  = 0000: No protected area
             *   Bit 1-0 (WEL/WIP): Read-only bits
             *
             * High Byte 0xC7 = Configuration Register (CR) - Written second
             *   Bit 7-6 (DC[1:0])  = 11: 10 dummy cycles, supports 120/133MHz
             *   Bit 5 (Reserved)   = 0
             *   Bit 4 (PBE)        = 0: Preamble bit disabled
             *   Bit 3 (TB)         = 0: Top area protect (default)
             *   Bit 2 (Reserved)   = 0
             *   Bit 1-0 (ODS[1:0]) = 00: 30Ω output driver strength (default), 11 is the default value of MX25U51245G (RD-RW612-BGA)
             *
             * Note: Although displayed as 0xC040, the WRSR instruction writes bytes in order:
             *       1st byte writes SR(0x40), 2nd byte writes CR(0xC0)
             */
            .deviceModeArg       = 0xC740,
            .configCmdEnable     = 0,
            .deviceType          = 0x1,
            .sflashPadType       = kSerialFlash_4Pads,
            .serialClkFreq       = 7,
            /* 16MB/128Mbits MX25L12845G */
            .sflashA1Size        = 0x1000000U,
            .sflashA2Size        = 0,
            .sflashB1Size        = 0,
            .sflashB2Size        = 0,
            /* LookUp Table (LUT) - FlexSPI command sequences
             *
             * LUT Index Format: [Sequence_ID * 4 + Instruction_Index]
             * - Each sequence can have up to 4 instructions (index 0-3)
             * - Sequence IDs are used by .deviceModeSeq and FlexSPI operations
             *
             * Standard Sequence ID assignments:
             *   Seq 0: Read (Fast Read Quad I/O)
             *   Seq 1: Read Status Register
             *   Seq 2: Write Status/Configuration Register (used by deviceModeSeq)
             *   Seq 3: Write Enable
             *   Seq 5: Sector Erase
             *   Seq 8: Block Erase
             *   Seq 9: Page Program
             *   Seq 11: Chip Erase
             */
            .lookupTable =
                {
                    /* Read */
                    [0] = FC_FLEXSPI_LUT_SEQ(FC_CMD_SDR, FC_FLEXSPI_1PAD, 0xEB, FC_RADDR_SDR, FC_FLEXSPI_4PAD, 0x18),
                    [1] = FC_FLEXSPI_LUT_SEQ(FC_DUMMY_SDR, FC_FLEXSPI_4PAD, 0x0A, FC_READ_SDR, FC_FLEXSPI_4PAD, 0x04),

                    /* Read Status */
                    [4 * 1 + 0] =
                        FC_FLEXSPI_LUT_SEQ(FC_CMD_SDR, FC_FLEXSPI_1PAD, 0x05, FC_READ_SDR, FC_FLEXSPI_1PAD, 0x04),

                    /* Write Status */
                    [4 * 2 + 0] =
                        FC_FLEXSPI_LUT_SEQ(FC_CMD_SDR, FC_FLEXSPI_1PAD, 0x01, FC_WRITE_SDR, FC_FLEXSPI_1PAD, 0x02),

                    /* Write Enable */
                    [4 * 3 + 0] =
                        FC_FLEXSPI_LUT_SEQ(FC_CMD_SDR, FC_FLEXSPI_1PAD, 0x06, FC_STOP_EXE, FC_FLEXSPI_1PAD, 0x00),

                    /* Sector erase */
                    [4 * 5 + 0] =
                        FC_FLEXSPI_LUT_SEQ(FC_CMD_SDR, FC_FLEXSPI_1PAD, 0x20, FC_RADDR_SDR, FC_FLEXSPI_1PAD, 0x18),

                    /* Block erase */
                    [4 * 8 + 0] =
                        FC_FLEXSPI_LUT_SEQ(FC_CMD_SDR, FC_FLEXSPI_1PAD, 0x52, FC_RADDR_SDR, FC_FLEXSPI_1PAD, 0x18),

                    /* Page program - Quad Page Program (0x38) for MX25L12845G */
                    [4 * 9 + 0] =
                        FC_FLEXSPI_LUT_SEQ(FC_CMD_SDR, FC_FLEXSPI_1PAD, 0x38, FC_RADDR_SDR, FC_FLEXSPI_4PAD, 0x18),
                    [4 * 9 + 1] =
                        FC_FLEXSPI_LUT_SEQ(FC_WRITE_SDR, FC_FLEXSPI_4PAD, 0x40, FC_STOP_EXE, FC_FLEXSPI_1PAD, 0x00),

                    /* chip erase */
                    [4 * 11 + 0] =
                        FC_FLEXSPI_LUT_SEQ(FC_CMD_SDR, FC_FLEXSPI_1PAD, 0x60, FC_STOP_EXE, FC_FLEXSPI_1PAD, 0x00),
                },
        },
    .pageSize           = 0x100,
    .sectorSize         = 0x1000,
    .ipcmdSerialClkFreq = 0,
    .blockSize          = 0x8000,
    .fcb_fill[0]        = 0xFFFFFFFF,
};
#endif /* BOOT_HEADER_ENABLE */

//
//

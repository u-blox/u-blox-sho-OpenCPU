# Linker Scripts

Linker file is part of the required pre-setup condition and must be updated together with the flash configuration and flash driver files (`flash_config.c` and `mflash_drv.c`).

Select the folder that matches your build environment:

| Toolchain / IDE | Folder | File type |
|---|---|---|
| ARMGCC (command-line `armgcc` build) | [`ARMGCC/`](ARMGCC/) | `.ld` |
| MCUXpresso IDE (managed build) | [`MCUXpressoIDE/`](MCUXpressoIDE/) | `.ldt` |

> **Important:** Env. toolchain uses its own linker file. MCUXpresso IDE uses `.ldt` files. ARMGCC uses `.ld` files. Don't mix them.

> **Pre-setup requirement:** The correct linker files are part of the project setup before building the application. They must match the module Flash density and the selected SDK toolchain.

## Folder Structure

```shell
.
├── ARMGCC
│   ├── Flash_8MB
│   │   └── RW612_flash.ld
│   ├── Flash_16MB
│   │   └── RW612_flash.ld
│   └── README.md
├── MCUXpressoIDE
│   ├── main_text.ldt
│   ├── main_data.ldt
│   ├── end_text.ldt
│   ├── symbols.ldt
│   └── README.md
└── README.md
```

## MCUXpresso IDE templates

The MCUXpresso IDE folder contains the linker script templates used by the managed build flow:

- `main_text.ldt`
- `main_data.ldt`
- `end_text.ldt`
- `symbols.ldt`

Copy these files into the project's `linkscripts` folder before building. This is part of the pre-setup requirement for MCUXpresso IDE projects.

---

## Support

If you encounter any issues, please refer to the SDK documentation or reach out for support.

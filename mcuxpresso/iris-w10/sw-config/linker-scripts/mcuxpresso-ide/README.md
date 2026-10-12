# MCUXpresso IDE Linker Templates

MCUXpressoIDE generates the final linker script from **linker script templates** (`.ldt`) and from the memory layout stored in the project.
use these templates files, when the application is built inside **MCUXpresso IDE**. 

## Available Templates

This folder contains the IRIS-W1 MCUXpresso linker templates:

- `main_text.ldt`
- `main_data.ldt`
- `end_text.ldt`
- `symbols.ldt`

These files are the replacement set for the MCUXpresso IDE build flow.

## Adding the Templates to a Project

1. Open the project in MCUXpresso IDE.
2. In the project tree, locate (or create) the `linkscripts` folder:

   ```text
   <project>/
   └── linkscripts/
       └── *.ldt
   ```

3. Copy the `.ldt` files from this folder into `<project>/linkscripts`.
4. Rebuild the project. The IDE regenerates the linker script from the templates.

> **Note:** Custom templates in `linkscripts` override the IDE defaults for that project only. They are not shared between projects.


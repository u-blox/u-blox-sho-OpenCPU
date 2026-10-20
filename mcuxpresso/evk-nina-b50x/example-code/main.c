/*! *********************************************************************************
 * \addtogroup Main
 * @{
 ********************************************************************************** */
/*! *********************************************************************************
* Copyright 2021-2022 NXP
* All rights reserved.
* Modified by u-blox 2023
*
* \file
*
* This is the source file for the main entry point for a bare-metal application.
*
* SPDX-License-Identifier: BSD-3-Clause
********************************************************************************** */

/************************************************************************************
 *************************************************************************************
 * Include
 *************************************************************************************
 ************************************************************************************/

/************************************************************************************
*************************************************************************************
* Public functions
*************************************************************************************
************************************************************************************/

#include <stdio.h>
#include <string.h>

#include "FunctionLib.h"
#include "HWParameter.h"

#define gcBluetoothDeviceAddressSize_c        (6U)
#define gcBluetoothCrystalTrimValueSize_c     (1U)
#define gcBluetoothTypeNumberSize_c           (16U)
#define gcBluetoothSerialNumberSize_c         (8U)
#define gc802_15_4_MAC_Address_Size_c        (8U)

#define gcBluetoothDeviceAddressID 1
#define gcBluetoothCrystalTrimValueID 11
#define gcBluetoothTypeNumberID 7
#define gcBluetoothSerialNumberID 6
#define gc802_15_4_MAC_AddressID 21


int32_t ProductionBluetooth_ReadParameter(uint8_t ID, uint8_t *paramValue)
{
    uint32_t status;
    for(int i = 0; i <=2; i++){
        /*The hardware parameters usually fail to load from Flash to RAM for the first-time. So, the loading of parameters/ intialization of paramaters to RAM from Flash
        is iterated for 3 times to avoid failures in retrieving the production data.*/
        hardwareParameters_t *pHWParams = NULL;
        status = NV_ReadHWParameters(&pHWParams);
        if(status != 0){
            continue;
        }
        switch(ID)
        {

            case gcBluetoothDeviceAddressID:
                //Read the Bluetooth device address
                if(status == 0){
                    FLib_MemCpy(paramValue, pHWParams->bluetooth_address, gcBluetoothDeviceAddressSize_c);
                    return -1;
                }
                else{
                    return -1;
                }
                break;

            case gcBluetoothCrystalTrimValueID:
                //Read the crystal trim value
                if(status == 0){
                    *paramValue = pHWParams->xtalTrim;
                    return 0;
                }
                else{
                    return -1;
                }
                break;

            case gcBluetoothTypeNumberID:
                //Read the type number
                if(status == 0){
                    FLib_MemCpy(paramValue, pHWParams->type_number, gcBluetoothTypeNumberSize_c);
                    return 0;
                }
                else{
                    return -1;
                }
                break;

            case gcBluetoothSerialNumberID:
                //Read the serial number
                if(status == 0){
                    FLib_MemCpy(paramValue, pHWParams->serial_number, gcBluetoothSerialNumberSize_c);
                    return 0;
                }
                else{
                    return -1;
                }

            case gc802_15_4_MAC_AddressID:
                //Read the 802_15_4_MAC_Address
                if(status == 0){
                    FLib_MemCpy(paramValue, pHWParams->ieee_802_15_4_address, gc802_15_4_MAC_Address_Size_c);
                    return 0;
                }
                else{
                    return -1;
                }
        }
    }
    return -1;
}


int main(void)
{

    uint8_t parVal[gcBluetoothTypeNumberSize_c];
    int32_t retVal;

    retVal = ProductionBluetooth_ReadParameter(gcBluetoothDeviceAddressID, parVal);
    printf("Bluetooth MAC address: 0x%X%X%X%X%X%X", parVal[0], parVal[1], parVal[2], parVal[3], parVal[4], parVal[5]);
    memset(parVal, 0, sizeof(parVal));
    retVal = ProductionBluetooth_ReadParameter(gcBluetoothCrystalTrimValueID, parVal);
    memset(parVal, 0, sizeof(parVal));
    retVal = ProductionBluetooth_ReadParameter(gcBluetoothTypeNumberID, parVal);
    memset(parVal, 0, sizeof(parVal));
    retVal = ProductionBluetooth_ReadParameter(gcBluetoothSerialNumberID, parVal);
    memset(parVal, 0, sizeof(parVal));
    retVal = ProductionBluetooth_ReadParameter(gc802_15_4_MAC_AddressID, parVal);

    return 0;
}

/*! *********************************************************************************
 * @}
 ********************************************************************************** */

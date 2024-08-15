/*
 * Copyright 2024 u-blox
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *  http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include <zephyr/types.h>
#include <stddef.h>
#include <errno.h>
#include <zephyr/kernel.h>
#include <zephyr/sys/printk.h>

#include <zephyr/bluetooth/bluetooth.h>
#include <zephyr/bluetooth/direction.h>
#include <zephyr/sys/byteorder.h>
#include <zephyr/sys/util.h>

/* Length of CTE in unit of 8[us]
*  Below intervals are a tradeoff between power consumption and the time
*  it takes for the scanner to start tracking this tag. Set it accordingly.
*/
#define CTE_LEN (0x14U)
/* Number of CTE send in single periodic advertising train */
#define PER_ADV_EVENT_CTE_COUNT 1

#define EDDYSTONE_INSTANCE_ID_LEN   6
#define EDDYSTONE_NAMESPACE_LENGTH 10

static void adv_sent_cb(struct bt_le_ext_adv *adv,
			struct bt_le_ext_adv_sent_info *info);

const static struct bt_le_ext_adv_cb adv_callbacks = {
	.sent = adv_sent_cb,
};

static struct bt_le_ext_adv *adv_set;

/* Below intervals are a tradeoff between power consumption and the time
 * it takes for the scanner to start tracking this tag. Set it accordingly.
*/
const static struct bt_le_adv_param param =
		BT_LE_ADV_PARAM_INIT(BT_LE_ADV_OPT_EXT_ADV |
				     BT_LE_ADV_OPT_USE_IDENTITY |
				     BT_LE_ADV_OPT_USE_NAME,
				     BT_GAP_ADV_FAST_INT_MIN_2 / 0.625,
					 BT_GAP_ADV_FAST_INT_MAX_2 / 0.625,
				     NULL);

static struct bt_le_ext_adv_start_param ext_adv_start_param = {
	.timeout = 0,
	.num_events = 0,
};

/* Set periodic advertisement interval*/
const static struct bt_le_per_adv_param per_adv_param = {
	.interval_min = BT_GAP_ADV_FAST_INT_MIN_2 / 1.25,
	.interval_max = BT_GAP_ADV_FAST_INT_MAX_2 / 1.25,
	.options = BT_LE_ADV_OPT_USE_TX_POWER,
};

#if defined(CONFIG_BT_DF_CTE_TX_AOD)
/* Example sequence of antenna switch patterns for antenna matrix designed by
 * Nordic. For more information about antenna switch patterns see README.rst.
 */
static uint8_t ant_patterns[] = {0x2, 0x0, 0x5, 0x6, 0x1, 0x4, 0xC, 0x9, 0xE,
				 0xD, 0x8, 0xA};
#endif /* CONFIG_BT_DF_CTE_TX_AOD */

struct bt_df_adv_cte_tx_param cte_params = { .cte_len = CTE_LEN,
					     .cte_count = PER_ADV_EVENT_CTE_COUNT,
#if defined(CONFIG_BT_DF_CTE_TX_AOD)
					     .cte_type = BT_DF_CTE_TYPE_AOD_2US,
					     .num_ant_ids = ARRAY_SIZE(ant_patterns),
					     .ant_ids = ant_patterns
#else
					     .cte_type = BT_DF_CTE_TYPE_AOA,
					     .num_ant_ids = 0,
					     .ant_ids = NULL
#endif /* CONFIG_BT_DF_CTE_TX_AOD */
};

static void adv_sent_cb(struct bt_le_ext_adv *adv,
			struct bt_le_ext_adv_sent_info *info)
{
	printk("Advertiser[%d] %p sent %d\n", bt_le_ext_adv_get_index(adv),
	       adv, info->num_sent);
}

/* Offsets of the different data in bt_data ad[] below */
#define ADV_DATA_OFFSET_NAMESPACE   4
#define ADV_DATA_OFFSET_INSTANCE    14
#define ADV_DATA_OFFSET_TX_POWER    3

#define MAC_ADDR_LEN 6
#define EMPTY_REGISTER  0xFFFFFFFF

static char *pDefaultGroupNamespace = "NINA-B4TAG";

/* Eddystone UID data in the extended advertising data */
static struct bt_data ad[] = {
    BT_DATA_BYTES(BT_DATA_FLAGS, BT_LE_AD_NO_BREDR),
    BT_DATA_BYTES(BT_DATA_UUID16_ALL, 0xaa, 0xfe),
    BT_DATA_BYTES(BT_DATA_SVC_DATA16,
                  0xaa, 0xfe, /* Eddystone UUID */
                  0x00, /* Eddystone-UID frame type */
                  0x00, /* TX Power */
                  'N', 'I', 'N', 'A', '-', 'B', '4', 'T', 'A', 'G', /* Namespace placeholder, will be replaced in init */
                  'i', 'n', 's', 't', 'a', 'e', /* Instance Id placeholder, will be replaced in init */
                  0x00, /* reserved */
                  0x00 /* reserved */
                 )
};

/* the data added in the payload of periodic advertisements.*/
static struct bt_data per_ad[] = {
	BT_DATA(BT_DATA_NAME_COMPLETE, CONFIG_BT_DEVICE_NAME, sizeof(CONFIG_BT_DEVICE_NAME) - 1),
};

/* Get local BT MAC address. Returns customer address if set in UICR, otherwise NRF address.*/
void utilGetBtAddr(bt_addr_le_t *addr)
{
    if (NRF_UICR->CUSTOMER[0] != EMPTY_REGISTER || NRF_UICR->CUSTOMER[1] != EMPTY_REGISTER) {
        addr->a.val[0] = (uint8_t)(NRF_UICR->CUSTOMER[1] >> 8);
        addr->a.val[1] = (uint8_t)NRF_UICR->CUSTOMER[1];
        addr->a.val[2] = (uint8_t)(NRF_UICR->CUSTOMER[0] >> 24);
        addr->a.val[3] = (uint8_t)(NRF_UICR->CUSTOMER[0] >> 16);
        addr->a.val[4] = (uint8_t)(NRF_UICR->CUSTOMER[0] >> 8);
        addr->a.val[5] = (uint8_t)NRF_UICR->CUSTOMER[0];

        addr->type = BT_ADDR_LE_PUBLIC;
    } else {
        *((uint8_t *)addr->a.val + 0) = (uint8_t)((NRF_FICR->DEVICEADDR[1] >> 8) | 0xC0);
        *((uint8_t *)addr->a.val + 1) = (uint8_t)NRF_FICR->DEVICEADDR[1];
        *((uint8_t *)addr->a.val + 2) = (uint8_t)(NRF_FICR->DEVICEADDR[0] >> 24);
        *((uint8_t *)addr->a.val + 3) = (uint8_t)(NRF_FICR->DEVICEADDR[0] >> 16);
        *((uint8_t *)addr->a.val + 4) = (uint8_t)(NRF_FICR->DEVICEADDR[0] >> 8);
        *((uint8_t *)addr->a.val + 5) = (uint8_t)(NRF_FICR->DEVICEADDR[0]);
        addr->type = BT_ADDR_LE_RANDOM;
    }
}

static uint8_t uuid[EDDYSTONE_INSTANCE_ID_LEN];

int main(void)
{
	char addr_s[BT_ADDR_LE_STR_LEN];
	struct bt_le_oob oob_local;
	int err;
    bt_addr_le_t addr;
    int8_t txPower = 4;

	printk("Starting u-blox Generic Aoa Tag App Demo\n");

	/* Initialize the Bluetooth Subsystem */
	printk("Bluetooth initialization...");
	err = bt_enable(NULL);
	if (err) {
		printk("failed (err %d)\n", err);
		return 0;
	}
	printk("success\n");

    utilGetBtAddr(&addr);
    memcpy(uuid, addr.a.val, MAC_ADDR_LEN);

    memcpy((uint8_t *)&ad[2].data[ADV_DATA_OFFSET_NAMESPACE], pDefaultGroupNamespace, EDDYSTONE_NAMESPACE_LENGTH);
    memcpy((uint8_t *)&ad[2].data[ADV_DATA_OFFSET_INSTANCE], uuid, EDDYSTONE_INSTANCE_ID_LEN);
    memcpy((uint8_t *)&ad[2].data[ADV_DATA_OFFSET_TX_POWER], &txPower, sizeof(txPower));

	printk("Create ext. adv...");
	err = bt_le_ext_adv_create(&param, &adv_callbacks, &adv_set);
	if (err) {
		printk("failed (err %d)\n", err);
		return 0;
	}
	printk("success\n");

    printk("Set ext adv data...");
    err = bt_le_ext_adv_set_data(adv_set, ad, ARRAY_SIZE(ad), NULL, 0);
    if (err) {
        printk("Failed setting ext adv data: %d\n", err);
    }
    printk("success\n");


	printk("Update CTE params...");
	err = bt_df_set_adv_cte_tx_param(adv_set, &cte_params);
	if (err) {
		printk("failed (err %d)\n", err);
		return 0;
	}
	printk("success\n");

	printk("Periodic advertising params set...");
	err = bt_le_per_adv_set_param(adv_set, &per_adv_param);
	if (err) {
		printk("failed (err %d)\n", err);
		return 0;
	}
	printk("success\n");

	printk("Enable CTE...");
	err = bt_df_adv_cte_tx_enable(adv_set);
	if (err) {
		printk("failed (err %d)\n", err);
		return 0;
	}
	printk("success\n");

	printk("Periodic advertising enable...");
	err = bt_le_per_adv_start(adv_set);
	if (err) {
		printk("failed (err %d)\n", err);
		return 0;
	}
	printk("success\n");

	printk("Extended advertising enable...");
	err = bt_le_ext_adv_start(adv_set, &ext_adv_start_param);
	if (err) {
		printk("failed (err %d)\n", err);
		return 0;
	}
	printk("success\n");

	/* Send data from the tag to the anchor/scanner using the payload of periodic advertisements */
	err = bt_le_per_adv_set_data(adv_set, per_ad, ARRAY_SIZE(per_ad));
	if (err) {
		printk("failed (err %d)\n", err);
		return 0;
	}
	printk("success\n");

	bt_le_ext_adv_oob_get_local(adv_set, &oob_local);
	bt_addr_le_to_str(&oob_local.addr, addr_s, sizeof(addr_s));

	printk("Started extended advertising as %s\n", addr_s);

	return 0;
}
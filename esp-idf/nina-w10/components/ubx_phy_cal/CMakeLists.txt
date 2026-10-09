
# Copyright 2021 u-blox
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#  http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set(COMPONENT_REQUIRES esp_wifi)  # required for esp-idf v5.1

# set(COMPONENT_PRIV_REQUIRES ubx_otp)

# set(COMPONENT_SRCS "ubx_phy_cal.c")
# set(COMPONENT_ADD_INCLUDEDIRS "include")

# register_component()

# esp-idf v5.1
idf_component_register(SRCS  "ubx_phy_cal.c"
                    INCLUDE_DIRS "include"
                    PRIV_REQUIRES ubx_otp esp_phy
                    )
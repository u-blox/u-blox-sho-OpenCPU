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

# esp-idf < v5.1 change to:
# set(COMPONENT_REQUIRES spi_flash)

# set(COMPONENT_SRCS "otp_is25lp.c otp_mx25.c otp_reader.c")
# set(COMPONENT_ADD_INCLUDEDIRS "include")
set(COMPONENT_NAME "ubx_otp")

# register_component()

# esp-idf v5.1
idf_component_register(SRCS  "otp_is25lp.c" "otp_mx25.c" "otp_reader.c"
                    INCLUDE_DIRS "include"
                    REQUIRES spi_flash
                    )
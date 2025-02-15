export VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/nvidia_icd.json
export __NV_PRIME_RENDER_OFFLOAD=1
export __GLX_VENDOR_LIBRARY_NAME=nvidia
export __VK_LAYER_NV_optimus=NVIDIA_only
export MESA_VK_DEVICE_SELECT=1  # Force discrete GPU

./AirSimNH/LinuxNoEditor/AirSimNH.sh -windowed
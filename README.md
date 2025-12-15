# Workspace Template for porting SiFli to Zephyr RTOS

## Usage

Go to one directory as your root, eg, `$HOME/Dev/Sifli`

### Preparation

```shell
# create a root directory of your workspace
mkdir workspace
cd workspace
```

### Install Python Dependencies and toolchain

    Please refer to official [zephyr document](https://docs.zephyrproject.org/latest/develop/getting_started/index.html) for detailed installation instructions

```shell
# gdb-py inside zephyr-sdk requires python 3.10, so need to setup python3.10 first
python -m venv .venv
. .venv/bin/activate
pip install west
```

```shell
git clone https://github.com/iotpi/sifli-porting-template.git
west init -l sifli-porting-template
# or use `west init -m https://github.com/iotpi/sifli-porting-template.git` instead

west update
west zephyr-export
west packages pip --install

pip install -r zephyr/scripts/requirements.txt

# install zephyr sdk if you didn't yet
west sdk install -t arm-zephyr-eabi

# To use PyCortexMDebug
git clone https://github.com/bnahill/PyCortexMDebug -b switch-to-cmsis_svd
pip install cmsis_svd
mkdir svd
cp PATH_TO_SIFLI_SDK/tools/svd_external/... to svd
setup .gdbinit and gdb.py as following
```

```.gdbinit
source gdb.py

source PyCortexMDebug/scripts/gdb.py
svd_load svd/SF32LB58x.svd
```

``` python
script_path = Path(os.path.abspath(os.path.expanduser(__file__)))
root_path = script_path.parents[0]
venv_path = root_path / 'venv/lib/python3.10/site-packages'
if venv_path.is_dir():
    sys.path.append(str(venv_path))
else:
    print("failed to add venv_path: ", venv_path)
```

clone zephyr porting repos:

```shell
git clone git@github.com:iotpi/sifli_zephyr.git
git clone git@github.com:iotpi/hal_sifli.git
```

## Build

```shell
# because following 'export' uses $PWD, so it should run under
# 'workspace' directory, or you need to change $PWD to your
# real root
export ZEPHYR_EXTRA_MODULES="$PWD/sifli_zephyr;$PWD/hal_sifli"
west build -p always -b sf32lb58_devkit/sf32lb586/hcpu zephyr/samples/hello_world/
west build -p always -b sf32lb58_devkit/sf32lb586/hcpu zephyr/samples/hello_world/ -- -DEXTRA_CONF_FILE=debug.conf
```

## Debug

```shell
probe-rs info --chip SF32LB58   --protocol swd --speed 4000
RUST_LOG="probe_rs::architecture::arm=debug,probe_rs::flashing::erase=debug" cargo run --  erase --chip SF32LB58   --protocol swd --speed 4000

cargo run -- download --chip SF32LB58 --base-address 0x1C020000 --binary-format bin bootloader.bin
cargo run -- download --chip SF32LB58 --base-address 0x18000000 --binary-format bin main.bin

JLinkExe -Device SF32LB58X -if swd -speed 4000
JLink> erase 0x18000000 0x18001000

JLinkGDBServer -Device SF32LB58X -if swd -speed 4000

```

## Access Debug Port, Access Port

```shell
# DP SELECT = 0x00000070
# AP register IDR
mon readapex 0x00000070 0xfc

# DPIDR
mon readdp 0
```

## Build Doc

```shell
python -m venv --prompt doc venv-docs
. venv-docs/bin/activate
pip install west
pip install -r zephyr/doc/requirements.txt
pip install jsonschema tabulate
cd zephyr/doc
make html-fast HW_FEATURES_VENDOR_FILTER=sifli
```

## Check Compilance
```shell
python zephyr/scripts/ci/check_compilance.py
```

## Emacs Magit

Added sign-off:

    Show commits
    (press) r(eword) w( reword a commit)
    C-c TAB (show options)
    s (sign-off)

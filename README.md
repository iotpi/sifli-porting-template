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

# install zephyr sdk if you didn't yet
west sdk install -t arm-zephyr-eabi
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
```

## Debug

```shell
probe-rs info --chip SF32LB58   --protocol swd --speed 4000
RUST_LOG="probe_rs::architecture::arm=debug,probe_rs::flashing::erase=debug" cargo run --  erase --chip SF32LB58   --protocol swd --speed 4000

JLinkExe -Device SF32LB58X -if swd -speed 4000
JLink> erase 0x18000000 0x18001000

JLinkGDBServer -Device SF32LB58X -if swd -speed 4000

```

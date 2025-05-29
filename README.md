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
west -l sifli-porting-template
west update
west zephyr-export
west packages pip --install

# install zephyr sdk if you didn't yet
west sdk install -t arm-zephyr-eabi
```

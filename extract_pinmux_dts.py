import sys
import pdfplumber
from operator import itemgetter

PREFIX = "SF32LB58"
NEWLINE = "\n"

MACRO_DEFINE = "ZEPHYR_INCLUDE_DT_BINDINGS_PINCTRL_SF32LB58_PINMUX_H_"

HPSYS_PINMUX_BASE_ADDR = 0x40003000
LPSYS_PINMUX_BASE_ADDR = 0x50003000

def output_file_header(f):
    f.write("/*" + NEWLINE)
    f.write(" * Copyright (c) 2025 Qingdao IotPi Ltd" + NEWLINE)
    f.write(" *" + NEWLINE)
    f.write(" * SPDX-License-Identifier: Apache-2.0" + NEWLINE)
    f.write(" *" + NEWLINE)
    f.write(" * This file is auto-generated from SF32LB58x User Manual" + NEWLINE)
    f.write(" */" + NEWLINE)
    f.write("" + NEWLINE)
    f.write("&pinmux {" + NEWLINE)

def output_file_footer(f):
    f.write("};" + NEWLINE)

def output_pinmux(pinmux_header_file, pinmux, regs, base_addr, subsys):
    pinmux_header_file.write("{0:<4}/* SF32LB58 {1} pinmux */".format(" ", subsys.upper()) + NEWLINE + NEWLINE)

    keys = sorted(pinmux.keys())

    for key in keys:
        func_array = pinmux[key]

        pinmux_header_file.write("{:<4}/* {} */".format(" ", key) + NEWLINE)
        func_array = sorted(func_array, key=itemgetter(4))
        for value in func_array:
            pin_num = value[0]
            pin_name = value[1]
            func = value[2]
            sel = value[3]

            pin_def = "_".join([func, pin_name])
            pad_def = "_".join([pin_name, func])
            pinmux_header_file.write("{0:<4}/omit-if-no-ref/ {1}: {2} {{".format(
                " ",
                pin_def.lower(),
                pad_def) + NEWLINE)
            reg = regs[pin_name]
            pinmux_header_file.write("{:<8}pinmux = <{} {}>;".format(" ", hex(base_addr + reg), sel) + NEWLINE)
            # line = "#define {0:<40} {1:<4} {2}".format(pin_def, int(sel), "/* Pin: {0} */".format(pin_num))
            # pinmux_header_file.write(line + NEWLINE)
            pinmux_header_file.write("{:<4}}};".format(" ") + NEWLINE)

        pinmux_header_file.write(NEWLINE)

def extract_pinmux(pdf, pages):
    pin_num = None
    pin_name = None
    pin_type = None

    pinmux = {}

    for p in pages:
        pdf_page = pdf.pages[p]
        pdf_table = pdf_page.extract_table()
        for row in pdf_table[2:]:
            if pin_num is None and row[0] is None:
                raise Exception("Pin number field is None")
            if row[0] is not None:
                # a new pin number pinmux started
                print("pinmux row: {}".format(row))
                pin_num = row[0]
                pin_name = row[1]
                try:
                    pin_type = row[2]
                except:
                    breakpoint()

            sel = row[3]
            if sel == 'Others':
                continue
            func = row[4]
            func = func.replace("#", "")

            func_pair = func.split("_")

            func_array = pinmux.get(func_pair[0])
            if func_array is None:
                func_array = []
                pinmux[func_pair[0]] = func_array

            sort_key = func_pair[0]
            if len(func_pair) > 1:
                sort_key = func_pair[1]
            pair = (pin_num, pin_name, func, sel, sort_key)
            func_array.append(pair)

    return pinmux

def extract_pad_registers(pdf, pages):
    regs = {}
    is_first = True
    for p in pages:
        pdf_page = pdf.pages[p]
        pdf_tables = pdf_page.extract_tables()
        if is_first:
            pdf_table = pdf_tables[len(pdf_tables) - 1]
            is_first = False
        else:
            pdf_table = pdf_tables[0]
        for row in pdf_table:
            if row[3].startswith("PAD_"):
                print("row: {}".format(row))
                pair = row[3].split("_")
                # print(pair)
                regs[pair[1]] = int(row[0], 16)
    return regs

if __name__ == "__main__":
    pdf = pdfplumber.open("../UM5801-SF32LB58x-用户手册 V0p3.pdf")

    hpsys_regs_pages = range(93, 126)
    hpsys_regs = extract_pad_registers(pdf, hpsys_regs_pages)

    hpsys_pinmux_pages = range(71, 81)
    hpsys_pinmux = extract_pinmux(pdf, hpsys_pinmux_pages)

    # output_pinmux(sys.stdout, hpsys_pinmux, regs, HPSYS_PINMUX_BASE_ADDR, "hpsys")
    # exit(0)

    # print(hpsys_pinmux)

    # import sys
    # output_pinmux(sys.stdout, hpsys_pinmux, "hpsys")
    # exit(0)

    lpsys_regs_pages = range(133, 150)
    lpsys_regs = extract_pad_registers(pdf, lpsys_regs_pages)

    lpsys_pinmux_pages = range(82, 88)
    lpsys_pinmux = extract_pinmux(pdf, lpsys_pinmux_pages)
    # print(lpsys_pinmux)

    with open("sf32lb58-hpsys-pinmux.dtsi", "w") as f:
        output_file_header(f)
        output_pinmux(f, hpsys_pinmux, hpsys_regs, HPSYS_PINMUX_BASE_ADDR, "hpsys")
        output_file_footer(f)

    with open("sf32lb58-lpsys-pinmux.dtsi", "w") as f:
        output_file_header(f)
        output_pinmux(f, lpsys_pinmux, lpsys_regs, LPSYS_PINMUX_BASE_ADDR, "lpsys")
        output_file_footer(f)

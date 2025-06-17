import win32print

printers = win32print.EnumPrinters(2)
print("Impressoras disponíveis:")
for printer in printers:
    print(f"- {printer[2]}")
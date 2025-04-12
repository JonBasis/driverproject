#include "utils.h"

VOID PrintChars(PCHAR chars, ULONG size) 
{
	for (ULONG i = 0; i < size && chars[i]; i++) {
		DbgPrint("%c", chars[i]);
	}
}


ULONG StringLengthSafe(PCHAR str, ULONG maxSize) 
{
	ULONG size = 0;
	while (str[size++]);

	return size <= maxSize ? size : maxSize;
}


VOID ConvertInt32ToIpString(UINT32 targetIp, PCHAR buffer, ULONG bufferSize) {
	NTSTATUS Status = RtlStringCchPrintfA(buffer, bufferSize, "%d.%d.%d.%d", (targetIp >> 3 * 8), (targetIp >> 2 * 8) & 0xFF, (targetIp >> 1 * 8) & 0xFF, targetIp & 0xFF);

	if (!NT_SUCCESS(Status)) {
		RtlZeroMemory(buffer, bufferSize);
	}
}
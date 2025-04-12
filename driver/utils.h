#pragma once
#include <ntifs.h>
#include <Ntstrsafe.h>

/*
util functions
*/

VOID PrintChars(PCHAR chars, ULONG size);

ULONG StringLengthSafe(PCHAR str, ULONG maxSize);

#define IP_STRING_SIZE 16
VOID ConvertInt32ToIpString(UINT32 targetIp, PCHAR buffer, ULONG bufferSize);
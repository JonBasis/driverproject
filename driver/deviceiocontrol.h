#pragma once
#include <ntifs.h>

#pragma warning(disable : 4201)

#include "utils.h"
#include "filtering.h"

#define PORTS_COUNT 65536
/*
IOCTL handler functions
*/

NTSTATUS IOCTLDriverTest(PIRP Irp, PCHAR inputBuffer, ULONG inputBufferLength, PCHAR outputBuffer, ULONG outputBufferLength);

NTSTATUS IOCTLDriverBlockIp(PIRP Irp, PUINT32 inputBuffer, ULONG inputBufferLength, PVOID outputBuffer, ULONG outputBufferLength, PDEVICE_OBJECT DeviceObject);

NTSTATUS IOCTLDriverUnblockIp(PIRP Irp, PUINT32 inputBuffer, ULONG inputBufferLength, PVOID outputBuffer, ULONG outputBufferLength, PDEVICE_OBJECT DeviceObject);

NTSTATUS IOCTLDriverBlockPort(PIRP Irp, PUINT16 inputBuffer, ULONG inputBufferLength, PVOID outputBuffer, ULONG outputBufferLength, PDEVICE_OBJECT DeviceObject);

NTSTATUS IOCTLDriverUnblockPort(PIRP Irp, PUINT16 inputBuffer, ULONG inputBufferLength, PVOID outputBuffer, ULONG outputBufferLength, PDEVICE_OBJECT DeviceObject);

NTSTATUS IOCTLDriverEnumIp(PIRP Irp, PUINT32 outputBuffer, ULONG outputBufferLength, PDEVICE_OBJECT DeviceObject);

NTSTATUS IOCTLDriverEnumPort(PIRP Irp, PUINT16 outputBuffer, ULONG outputBufferLength, PDEVICE_OBJECT DeviceObject);
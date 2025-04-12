#pragma once

#pragma warning(disable : 4201)

#include <ntifs.h>
#define INITGUID
#include <fwpmk.h>
#include <ndis/nbl.h>
#include <fwpsk.h>

#define PORTS_COUNT 65536


typedef enum _ipEnumResponseType {
	IP_ARRAY_SIZE = 0,
	IP_ARRAY_DATA = 1,

} ipEnumResponseType;


typedef struct _ipEnumResponseHeader {
	ipEnumResponseType type;
	DWORD dataSize;

} ipEnumResponseHeader, *PipEnumResponseHeader;


/*
driver entry util functions
*/

NTSTATUS StartupWfp(PDEVICE_OBJECT DeviceObject);

NTSTATUS GetEngineHandle(VOID);

VOID CloseEngineHandle(VOID);

VOID CleanupWfp(VOID);

/*
deviceiocontrol util functions
*/

VOID BlockIpClassify(const FWPS_INCOMING_VALUES* inFixedValues, const FWPS_INCOMING_METADATA_VALUES* inMetaValues,
	PVOID layerData, const VOID* classifyContext, const FWPS_FILTER* filter, UINT64 flowContext, FWPS_CLASSIFY_OUT* classifyOut);

NTSTATUS BlockIpNotify(FWPS_CALLOUT_NOTIFY_TYPE notifyType, const GUID* filterKey, FWPS_FILTER3* filter);

VOID BlockIpFlowDelete(UINT16 layerId1, UINT32 calloutId1, UINT64 flowContext);

NTSTATUS BlockIpTraffic(UINT32 targetIp);

NTSTATUS UnblockIpTraffic(UINT32 targetIp);

NTSTATUS BlockPortTraffic(UINT16 targetPort);

NTSTATUS UnblockPortTraffic(UINT16 targetPort);

NTSTATUS EnumIp(PUINT32 outputBuffer, ULONG outputBufferLength, ULONG_PTR* bytesWritten);

NTSTATUS EnumPort(PUINT16 outputBuffer, ULONG outputBufferLength, ULONG_PTR* bytesWritten);
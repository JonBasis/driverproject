#include "filtering.h"

DEFINE_GUID(IP_BLOCKING_CALLOUT, 0x13cf4a14, 0xa631, 0x46c9, 0xa2, 0xc7, 0xc8, 0x41, 0xc3, 0x8e, 0x6b, 0x95);
UINT32 calloutId;

UINT64 filterId;
DEFINE_GUID(IP_BLOCKING_SUBLAYER, 0x227d6ba0, 0x1714, 0x4313, 0x81, 0xb1, 0x07, 0x20, 0x2f, 0x39, 0xfb, 0xdd);

HANDLE hEngineHandle;

BOOL isBlocking = FALSE;

PipEntry ipArray;
KSPIN_LOCK portArrayLock;
portEntry portArray[PORTS_COUNT];


//
// handle memory pool utils

KSPIN_LOCK ipArrayLock;

//actual array size
SIZE_T ipArraySize;

//element count
DWORD lastIpElement;

//
//


/*
driver entry util functions
*/

NTSTATUS RegisterIpFilterCallout(PDEVICE_OBJECT DeviceObject) {
	NTSTATUS Status = STATUS_SUCCESS;

	FWPS_CALLOUT callout = { 0 };
	callout.calloutKey = IP_BLOCKING_CALLOUT;

	callout.flags = 0;

	callout.classifyFn = BlockIpClassify;

	callout.notifyFn = BlockIpNotify;
	callout.flowDeleteFn = BlockIpFlowDelete;


	Status = FwpsCalloutRegister(DeviceObject, &callout, &calloutId);
	if (!NT_SUCCESS(Status)) {
		DbgPrint("[-] failed registering callout, error %ld\n", Status);
		return Status;
	}

	FWPM_CALLOUT fwpmCallout = { 0 };
	fwpmCallout.calloutKey = IP_BLOCKING_CALLOUT;
	fwpmCallout.displayData.name = L"IP BLOCKING CALLOUT";
	fwpmCallout.displayData.description = L"CUSTOM IP BLOCKING CALLOUT";
	fwpmCallout.applicableLayer = FWPM_LAYER_STREAM_V4;
	fwpmCallout.flags = 0;


	Status = FwpmCalloutAdd(hEngineHandle, &fwpmCallout, NULL, NULL);
	if (!NT_SUCCESS(Status)) {
		DbgPrint("[-] failed adding callout to engine, error %ld\n", Status);
		FwpsCalloutUnregisterById(calloutId);
		return Status;
	}

	return Status;
}


NTSTATUS RegisterSublayer(VOID) {
	NTSTATUS Status = STATUS_SUCCESS;

	FWPM_SUBLAYER filteringSublayer = { 0 };
	filteringSublayer.subLayerKey = IP_BLOCKING_SUBLAYER;

	filteringSublayer.displayData.name = L"IP BLOCKING SUBLAYER";
	filteringSublayer.displayData.description = L"CUSTOM IP BLOCKING SUBLAYER";

	filteringSublayer.flags = 0;

	filteringSublayer.weight = 100;


	Status = FwpmSubLayerAdd(hEngineHandle, &filteringSublayer, NULL);
	if (!NT_SUCCESS(Status)) {
		DbgPrint("[-] failed adding sublayer, error %ld\n", Status);
		return Status;
	}

	return Status;
}


NTSTATUS RegisterIpFilter(VOID) {
	NTSTATUS Status = STATUS_SUCCESS;

	FWPM_FILTER filter = { 0 };
	filter.displayData.name = L"IP BLOCKING FILTER";
	filter.displayData.description = L"CUSTOM IP BLOCKING FILTER";
	filter.flags = 0;
	filter.layerKey = FWPM_LAYER_STREAM_V4;
	filter.subLayerKey = IP_BLOCKING_SUBLAYER;
	filter.weight.type = FWP_EMPTY;

	filter.numFilterConditions = 1;
	FWPM_FILTER_CONDITION conditions[1];

	conditions[0].fieldKey = FWPM_CONDITION_IP_REMOTE_ADDRESS;
	conditions[0].matchType = FWP_MATCH_GREATER_OR_EQUAL;
	conditions[0].conditionValue.type = FWP_UINT32;
	conditions[0].conditionValue.uint32 = 0;

	filter.filterCondition = conditions;
	filter.action.type = FWP_ACTION_CALLOUT_UNKNOWN;
	filter.action.calloutKey = IP_BLOCKING_CALLOUT;

	Status = FwpmFilterAdd(hEngineHandle, &filter, NULL, NULL);
	if (!NT_SUCCESS(Status))
		DbgPrint("[-] failed adding filter, error %ld\n", Status);

	filterId = filter.filterId;

	return Status;
}


VOID DeleteCallout(VOID) {
	NTSTATUS Status = STATUS_SUCCESS;

	Status = FwpmCalloutDeleteById(hEngineHandle, calloutId);
}


VOID DeleteSublayer(VOID) {
	NTSTATUS Status = STATUS_SUCCESS;

	Status = FwpmSubLayerDeleteByKey(hEngineHandle, &IP_BLOCKING_SUBLAYER);
}


VOID DeleteFilter(VOID) {
	NTSTATUS Status = STATUS_SUCCESS;

	Status = FwpmFilterDeleteById(hEngineHandle, filterId);
}


VOID PrintIpArray(VOID) {
	DbgPrint("ipArray: [\n");
	for (SIZE_T i = 0; i < lastIpElement; i++) {
		DbgPrint("(%u, %u), ", ipArray[i].ip, ipArray[i].packetCount);
	}
	DbgPrint("\n]\n");
}


NTSTATUS SetupIpArray(VOID) {
	ipArray = ExAllocatePool2(POOL_FLAG_NON_PAGED, ipArraySize * sizeof(ipEntry), 'GINN');
	if (!ipArray) {
		DbgPrint("[-] failed to allocate ip array\n");
		return STATUS_INSUFFICIENT_RESOURCES;
	}

	return STATUS_SUCCESS;
}


NTSTATUS DoubleIpArray(VOID) {
	NTSTATUS Status = STATUS_SUCCESS;
	KIRQL oldIrql;

	KeAcquireSpinLock(&ipArrayLock, &oldIrql);

	DbgPrint("[+] doubling ip array\n");

	if (ipArraySize * 2 < ipArraySize) {
		Status = STATUS_INSUFFICIENT_RESOURCES;
		goto Done;
	}

	PipEntry newIpArray = ExAllocatePool2(POOL_FLAG_NON_PAGED, ipArraySize * 2 * sizeof(ipEntry), 'GGIN');
	if (!newIpArray) {
		DbgPrint("[-] failed reallocating memory for ip array\n");
		Status = STATUS_INSUFFICIENT_RESOURCES;
		goto Done;
	}

	RtlZeroMemory(newIpArray, ipArraySize * 2 * sizeof(ipEntry));
	RtlCopyMemory(newIpArray, ipArray, ipArraySize * sizeof(ipEntry));
	
	ExFreePoolWithTag(ipArray, 'GGIN');
	ipArray = newIpArray;

	ipArraySize *= 2;

	Done:
	KeReleaseSpinLock(&ipArrayLock, oldIrql);
	DbgPrint("[+] finished doubling ip array\n");
	return Status;
}


VOID SetupPortArray(VOID) {
	RtlZeroMemory(portArray, sizeof(portArray));
}


VOID DeleteIpArray(VOID) {
	ExFreePoolWithTag(ipArray, 'GGIN');
}


NTSTATUS StartupWfp(PDEVICE_OBJECT DeviceObject) {
	NTSTATUS Status = STATUS_SUCCESS;

	DbgPrint("[+] StartupWfp\n");
	Status = GetEngineHandle();
	if (!NT_SUCCESS(Status)) return Status;

	DbgPrint("[+] got handle, registering callout\n");
	Status = RegisterIpFilterCallout(DeviceObject);
	if (!NT_SUCCESS(Status)) {
		CloseEngineHandle();
		return Status;
	}

	DbgPrint("[+] registered callout, registering sublayer\n");
	Status = RegisterSublayer();
	if (!NT_SUCCESS(Status)) {
		DeleteCallout();
		CloseEngineHandle();
		return Status;
	}

	DbgPrint("[+] registered sublayer, registring filter\n");
	Status = RegisterIpFilter();
	if (!NT_SUCCESS(Status)) {
		DeleteSublayer();
		DeleteCallout();
		CloseEngineHandle();
		return Status;
	}

	ipArraySize = 16;
	DbgPrint("[+] filter registered, allocating memory for ip array\n");
	Status = SetupIpArray();
	if (!NT_SUCCESS(Status)) {
		DeleteFilter();
		DeleteSublayer();
		DeleteCallout();
		CloseEngineHandle();
		return Status;
	}

	DbgPrint("[+] ip array allocated, zeroing out port array\n");
	SetupPortArray();


	KeInitializeSpinLock(&portArrayLock);
	KeInitializeSpinLock(&ipArrayLock);

	lastIpElement = 0;

	DbgPrint("[+] all done in StartupWfp!\n");
	return Status;
}


VOID CleanupWfp(VOID) {
	DbgPrint("[+] CleanupWfp\n");

	DeleteIpArray();
	DeleteFilter();
	DeleteCallout();
	DeleteSublayer();
	CloseEngineHandle();
}


NTSTATUS GetEngineHandle(VOID) {
	NTSTATUS Status = STATUS_SUCCESS;

	if (!hEngineHandle) {
		Status = FwpmEngineOpen(NULL, RPC_C_AUTHN_WINNT, NULL, NULL, &hEngineHandle);

		if (!NT_SUCCESS(Status))
			DbgPrint("[-] failed getting a handle to the fwp engine, error: %ld\n", Status);
	}


	return Status;
}


VOID CloseEngineHandle(VOID) {
	NTSTATUS Status = STATUS_SUCCESS;

	Status = FwpmEngineClose(hEngineHandle);

	if (!NT_SUCCESS(Status))
		DbgPrint("[-] failed closing engine handle, error %ld\n", Status);
}


/*
deviceiocontrol util functions
*/

BOOL IpInArray(UINT32 ip) {
	BOOL exists = FALSE;
	KIRQL oldIrql;

	KeAcquireSpinLock(&ipArrayLock, &oldIrql);

	for (SIZE_T i = 0; i < lastIpElement; i++) {
		if (ipArray[i].ip == ip) {
			exists = TRUE;
			ipArray[i].packetCount++;
			goto Done;
		}
	}

	Done:
	KeReleaseSpinLock(&ipArrayLock, oldIrql);
	return exists;
}


NTSTATUS InsertIp(UINT32 ip) {
	NTSTATUS Status = STATUS_SUCCESS;


	if (IpInArray(ip)) {
		goto Done2;
	}

	if (lastIpElement >= ipArraySize) {
		DbgPrint("[+] doubling ip array size\n");
		Status = DoubleIpArray();
		if (!NT_SUCCESS(Status)) goto Done2;
	}


	DbgPrint("[+] acquiring lock\n");
	KIRQL oldIrql = 0;
	KeAcquireSpinLock(&ipArrayLock, &oldIrql);

	DbgPrint("[+] lock acquired\n");

	DbgPrint("[+] lastIpElement: %ld\n", lastIpElement);
	ipEntry IpEntry = { ip, 0 };
	ipArray[lastIpElement] = IpEntry;
	lastIpElement++;

	PrintIpArray();
	KeReleaseSpinLock(&ipArrayLock, oldIrql);

	Done2:
	DbgPrint("[+] InsertIp done\n");
	return Status;
}


VOID DeleteIpFromArray(UINT32 ip) {
	KIRQL oldIrql = 0;
	KeAcquireSpinLock(&ipArrayLock, &oldIrql);

	for (SIZE_T i = 0; i < lastIpElement; i++) {
		if (ipArray[i].ip == ip) {
			for (SIZE_T j = i; j < lastIpElement; j++) {
				ipArray[j] = ipArray[j + 1];
			}

			lastIpElement--;
		}
	}

	DbgPrint("[+] ipArray after shift:[\n");
	for (SIZE_T i = 0; i < lastIpElement; i++) {
		DbgPrint("%u, ", ipArray[i].ip);
	}
	DbgPrint("\n]\n");

	KeReleaseSpinLock(&ipArrayLock, oldIrql);
}


VOID InsertPortToArray(UINT16 port) {
	KIRQL oldIrql = 0;
	KeAcquireSpinLock(&portArrayLock, &oldIrql);

	if (!portArray[port].port) {
		portArray[port].packetCount = 0;
	}
	portArray[port].port = 1;

	KeReleaseSpinLock(&portArrayLock, oldIrql);
}


VOID DeletePortFromArray(UINT16 port) {
	KIRQL oldIrql = 0;
	KeAcquireSpinLock(&portArrayLock, &oldIrql);

	portArray[port].port = 0;
	portArray[port].packetCount = 0;

	KeReleaseSpinLock(&portArrayLock, oldIrql);
}


BOOL PortInArray(UINT16 port) {
	KIRQL oldIrql = 0;
	KeAcquireSpinLock(&portArrayLock, &oldIrql);

	BOOL inArray = FALSE;

	if (portArray[port].port) {
		inArray = TRUE;
		portArray[port].packetCount++;
	}

	KeReleaseSpinLock(&portArrayLock, oldIrql);

	return inArray;
}


VOID GetSourceDestIp(const FWPS_INCOMING_VALUES* inFixedValues, PUINT32 sourceIp, PUINT32 destIp) {
	*sourceIp = inFixedValues->incomingValue[FWPS_FIELD_STREAM_V4_IP_LOCAL_ADDRESS].value.uint32;
	*destIp = inFixedValues->incomingValue[FWPS_FIELD_STREAM_V4_IP_REMOTE_ADDRESS].value.uint32;
}


VOID GetSourceDestPort(const FWPS_INCOMING_VALUES* inFixedValues, PUINT16 sourcePort, PUINT16 destPort) {
	*sourcePort = inFixedValues->incomingValue[FWPS_FIELD_STREAM_V4_IP_LOCAL_PORT].value.uint16;
	*destPort = inFixedValues->incomingValue[FWPS_FIELD_STREAM_V4_IP_REMOTE_PORT].value.uint16;
}


VOID CopyIpArrayToArray(PipEntry arrayOut, ULONG_PTR* bytesWritten) {
	DbgPrint("[+] copying ip array\n");

	DWORD arrayOutWrittenBytes = lastIpElement * sizeof(ipEntry);

	RtlZeroMemory(arrayOut, arrayOutWrittenBytes);
	RtlCopyMemory(arrayOut, ipArray, arrayOutWrittenBytes);

	DbgPrint("array copied:\n");
	for (DWORD i = 0; i < lastIpElement; i++) {
		DbgPrint("(%u, %u), ", ipArray[i].ip, ipArray[i].packetCount);
	}
	DbgPrint("\n");

	DbgPrint("array after copy:\n");
	for (DWORD i = 0; i < lastIpElement; i++) {
		DbgPrint("(%u, %u), ", arrayOut[i].ip, arrayOut[i].packetCount);
	}
	DbgPrint("\n");
	*bytesWritten += arrayOutWrittenBytes;
}


VOID CopyPortArrayToArray(PportEntry arrayOut, ULONG_PTR* bytesWritten) {
	KIRQL oldIrql = 0;

	KeAcquireSpinLock(&portArrayLock, &oldIrql);

	DbgPrint("[+] copying port array\n");

	RtlCopyMemory(arrayOut, portArray, PORTS_COUNT * sizeof(portEntry));
	*(PULONG)bytesWritten = (ULONG)(PORTS_COUNT * sizeof(portEntry));

	KeReleaseSpinLock(&portArrayLock, oldIrql);
}


VOID BlockIpClassify(const FWPS_INCOMING_VALUES* inFixedValues, const FWPS_INCOMING_METADATA_VALUES* inMetaValues, 
					PVOID layerData, const VOID* classifyContext, const FWPS_FILTER* filter, UINT64 flowContext, FWPS_CLASSIFY_OUT* classifyOut)
{
	UNREFERENCED_PARAMETER(inMetaValues);
	UNREFERENCED_PARAMETER(classifyContext);
	UNREFERENCED_PARAMETER(filter);
	UNREFERENCED_PARAMETER(flowContext);
	UNREFERENCED_PARAMETER(inFixedValues);
	FWPS_STREAM_CALLOUT_IO_PACKET* packets;


	packets = (FWPS_STREAM_CALLOUT_IO_PACKET*)layerData;
	RtlZeroMemory(classifyOut, sizeof(FWPS_CLASSIFY_OUT));

	classifyOut->actionType = FWP_ACTION_PERMIT;

	UINT32 sourceIp;
	UINT32 destIp;
	GetSourceDestIp(inFixedValues, &sourceIp, &destIp);

	UINT16 sourcePort;
	UINT16 destPort;
	GetSourceDestPort(inFixedValues, &sourcePort, &destPort);

	if (isBlocking && (IpInArray(sourceIp) || IpInArray(destIp))) {
		classifyOut->actionType = FWP_ACTION_BLOCK;
	}

	if (isBlocking && (PortInArray(sourcePort) || PortInArray(destPort))) {
		classifyOut->actionType = FWP_ACTION_BLOCK;
	}
}


NTSTATUS BlockIpNotify(FWPS_CALLOUT_NOTIFY_TYPE notifyType, const GUID* filterKey, FWPS_FILTER3* filter) {
	UNREFERENCED_PARAMETER(notifyType);
	UNREFERENCED_PARAMETER(filterKey);
	UNREFERENCED_PARAMETER(filter);

	return STATUS_SUCCESS;
}


VOID BlockIpFlowDelete(UINT16 layerId1, UINT32 calloutId1, UINT64 flowContext) {
	UNREFERENCED_PARAMETER(layerId1);
	UNREFERENCED_PARAMETER(calloutId1);
	UNREFERENCED_PARAMETER(flowContext);
}


NTSTATUS BlockIpTraffic(UINT32 targetIp) {
	NTSTATUS Status = STATUS_SUCCESS;

	DbgPrint("[+] blocking ip %u\n", targetIp);

	Status = InsertIp(targetIp);
	if (!NT_SUCCESS(Status)) {
		return Status;
	}

	isBlocking = TRUE;

	DbgPrint("[+] %u ip blocked\n", targetIp);

	return Status;
}


NTSTATUS UnblockIpTraffic(UINT32 targetIp) {
	NTSTATUS Status = STATUS_SUCCESS;

	DbgPrint("[+] unblocking ip %u\n", targetIp);

	DeleteIpFromArray(targetIp);

	DbgPrint("[+] %u ip unblocked\n", targetIp);

	return Status;
}


NTSTATUS BlockPortTraffic(UINT16 targetPort) {
	NTSTATUS Status = STATUS_SUCCESS;

	DbgPrint("[+] blocking port %u\n", targetPort);

	InsertPortToArray(targetPort);

	isBlocking = TRUE;

	DbgPrint("[+] %u port blocked\n", targetPort);

	return Status;
}


NTSTATUS UnblockPortTraffic(UINT16 targetPort) {
	NTSTATUS Status = STATUS_SUCCESS;

	DbgPrint("[+] unblocking port %u\n", targetPort);

	DeletePortFromArray(targetPort);

	DbgPrint("[+] %u port unblocked\n", targetPort);

	return Status;
}


NTSTATUS EnumIp(PipEntry outputBuffer, ULONG outputBufferLength, ULONG_PTR* bytesWritten) {
	NTSTATUS Status = STATUS_SUCCESS;

	KIRQL oldIrql = 0;

	KeAcquireSpinLock(&ipArrayLock, &oldIrql);

	PrintIpArray();
	DbgPrint("[+] outputBufferLength: %ld\n", outputBufferLength);

	if (outputBufferLength < sizeof(ipEnumResponseHeader)) {
		DbgPrint("[-] STATUS_INSUFFICIENT_RESOURCES, output buffer too small: %u\n", outputBufferLength);
		Status = STATUS_BUFFER_TOO_SMALL;
		goto Done;
	}


	PipEnumResponseHeader responseHeader = (PipEnumResponseHeader)outputBuffer;
	responseHeader->dataSize = lastIpElement * sizeof(ipEntry);
	responseHeader->type = IP_ARRAY_DATA;
	*bytesWritten = sizeof(ipEnumResponseHeader);

	if (lastIpElement == 0) goto Done;


	SIZE_T responseSize = sizeof(ipEnumResponseHeader) + lastIpElement * sizeof(ipEntry);

	if (outputBufferLength < responseSize) {
		responseHeader->type = IP_ARRAY_SIZE;
		*bytesWritten = sizeof(ipEnumResponseHeader);
		
		goto Done;
	}


	DbgPrint("[+] enumerating ips\n");

	PipEntry actualIpArrayStart = outputBuffer + sizeof(ipEnumResponseHeader) / sizeof(ipEntry);
	CopyIpArrayToArray(actualIpArrayStart, bytesWritten);

	Done:
	KeReleaseSpinLock(&ipArrayLock, oldIrql);

	return Status;
}


NTSTATUS EnumPort(PportEntry outputBuffer, ULONG outputBufferLength, ULONG_PTR* bytesWritten) {
	NTSTATUS Status = STATUS_SUCCESS;

	if (outputBufferLength < PORTS_COUNT * sizeof(portEntry)) {
		return STATUS_BUFFER_TOO_SMALL;
	}

	DbgPrint("[+] enumerating ports\n");

	CopyPortArrayToArray(outputBuffer, bytesWritten);

	return Status;
}
#include "deviceiocontrol.h"



NTSTATUS IOCTLDriverTest(PIRP Irp, PCHAR inputBuffer, ULONG inputBufferLength, PCHAR outputBuffer, ULONG outputBufferLength) 
{
	NTSTATUS Status = STATUS_SUCCESS;

	DbgPrint("[+] recieved from usermode: (\"");
	PrintChars(inputBuffer, inputBufferLength);
	DbgPrint("\")\n");

	PCHAR response = "Hello from driver!\n";
	ULONG responseSize = StringLengthSafe(response, outputBufferLength);

	RtlCopyBytes(outputBuffer, response, responseSize);
	DbgPrint("[+] sent response to usermode\n");

	Irp->IoStatus.Information = responseSize;

	return Status;
}


VOID DbgPrintIp(UINT32 ip) {
	CHAR IpString[IP_STRING_SIZE];
	ConvertInt32ToIpString(ip, IpString, sizeof(IpString));
	DbgPrint("[+] recieved ip: %s\n", IpString);
}


VOID DbgPrintPort(UINT16 port) {
	DbgPrint("[+] recieved port: %u\n", port);
}


NTSTATUS IOCTLDriverBlockIp(PIRP Irp, PUINT32 inputBuffer, ULONG inputBufferLength, PVOID outputBuffer, ULONG outputBufferLength, PDEVICE_OBJECT DeviceObject) {
	NTSTATUS Status = STATUS_SUCCESS;

	UNREFERENCED_PARAMETER(outputBuffer);
	UNREFERENCED_PARAMETER(outputBufferLength);
	UNREFERENCED_PARAMETER(DeviceObject);

	Irp->IoStatus.Information = 0;

	if (inputBufferLength != sizeof(UINT32) || outputBufferLength > 0) {
		DbgPrint("[-] recieved buffer size is invalid\n");
		return STATUS_INVALID_PARAMETER;
	}

	if (!NT_SUCCESS(Status)) return Status;

	UINT32 targetIp = inputBuffer[0];

	DbgPrintIp(targetIp);

	Status = BlockIpTraffic(targetIp);
	if (!NT_SUCCESS(Status)) {
		DbgPrint("[-] failed to block ip traffic, error: %ld\n", Status);
		return Status;
	}

	return Status;
}


NTSTATUS IOCTLDriverUnblockIp(PIRP Irp, PUINT32 inputBuffer, ULONG inputBufferLength, PVOID outputBuffer, ULONG outputBufferLength, PDEVICE_OBJECT DeviceObject) {
	NTSTATUS Status = STATUS_SUCCESS;

	UNREFERENCED_PARAMETER(outputBuffer);
	UNREFERENCED_PARAMETER(outputBufferLength);
	UNREFERENCED_PARAMETER(DeviceObject);

	Irp->IoStatus.Information = 0;

	if (inputBufferLength != sizeof(UINT32) || outputBufferLength > 0) {
		DbgPrint("[-] recieved buffer size is invalid\n");
		return STATUS_INVALID_PARAMETER;
	}

	if (!NT_SUCCESS(Status)) return Status;
	UINT32 targetIp = inputBuffer[0];

	DbgPrintIp(targetIp);

	Status = UnblockIpTraffic(targetIp);
	if (!NT_SUCCESS(Status)) {
		DbgPrint("[-] failed to unblock ip traffic, error: %ld\n", Status);
		return Status;
	}

	return Status;
}


NTSTATUS IOCTLDriverBlockPort(PIRP Irp, PUINT16 inputBuffer, ULONG inputBufferLength, PVOID outputBuffer, ULONG outputBufferLength, PDEVICE_OBJECT DeviceObject) {
	NTSTATUS Status = STATUS_SUCCESS;

	UNREFERENCED_PARAMETER(outputBuffer);
	UNREFERENCED_PARAMETER(outputBufferLength);
	UNREFERENCED_PARAMETER(DeviceObject);

	Irp->IoStatus.Information = 0;

	if (inputBufferLength != sizeof(UINT16) || outputBufferLength > 0) {
		DbgPrint("[-] recieved buffer size is invalid\n");
		return STATUS_BUFFER_TOO_SMALL;
	}

	if (!NT_SUCCESS(Status)) return Status;
	UINT16 targetPort = inputBuffer[0];

	DbgPrintPort(targetPort);

	Status = BlockPortTraffic(targetPort);
	if (!NT_SUCCESS(Status)) {
		DbgPrint("[-] failed to block port traffic, error: %ld\n", Status);
		return Status;
	}

	return Status;
}


NTSTATUS IOCTLDriverUnblockPort(PIRP Irp, PUINT16 inputBuffer, ULONG inputBufferLength, PVOID outputBuffer, ULONG outputBufferLength, PDEVICE_OBJECT DeviceObject) {
	NTSTATUS Status = STATUS_SUCCESS;

	UNREFERENCED_PARAMETER(outputBuffer);
	UNREFERENCED_PARAMETER(outputBufferLength);
	UNREFERENCED_PARAMETER(DeviceObject);

	Irp->IoStatus.Information = 0;

	if (inputBufferLength != sizeof(UINT16) || outputBufferLength > 0) {
		DbgPrint("[-] recieved buffer size is invalid\n");
		return STATUS_BUFFER_TOO_SMALL;
	}

	if (!NT_SUCCESS(Status)) return Status;
	UINT16 targetPort = inputBuffer[0];

	DbgPrintPort(targetPort);

	Status = UnblockPortTraffic(targetPort);
	if (!NT_SUCCESS(Status)) {
		DbgPrint("[-] failed to unblock port traffic, error: %ld\n", Status);
		return Status;
	}

	return Status;
}


NTSTATUS IOCTLDriverEnumIp(PIRP Irp, PipEntry outputBuffer, ULONG outputBufferLength, PDEVICE_OBJECT DeviceObject) {
	NTSTATUS Status = STATUS_SUCCESS;
	UNREFERENCED_PARAMETER(DeviceObject);

	Irp->IoStatus.Information = 0;

	Status = EnumIp(outputBuffer, outputBufferLength, &Irp->IoStatus.Information);
	DbgPrint("[+] Irp->IoStatus.Information = %llu\n", Irp->IoStatus.Information);

	if (!NT_SUCCESS(Status)){
		DbgPrint("[-] failed to enum ips, error: %ld\n", Status);
	}

	DbgPrint("array:\n");
	for (ULONG i = 0; i < outputBufferLength; i++) {
		DbgPrint("%u, ", outputBuffer[i].ip);
	}
	DbgPrint("\n");
	return Status;
}


NTSTATUS IOCTLDriverEnumPort(PIRP Irp, PportEntry outputBuffer, ULONG outputBufferLength, PDEVICE_OBJECT DeviceObject) {
	NTSTATUS Status = STATUS_SUCCESS;
	UNREFERENCED_PARAMETER(DeviceObject);

	if (outputBufferLength < PORTS_COUNT * sizeof(portEntry)) {
		DbgPrint("[-] recieved buffer size is invalid\n");
		Irp->IoStatus.Information = 0;
		return STATUS_BUFFER_TOO_SMALL;
	}


	Status = EnumPort(outputBuffer, outputBufferLength, &Irp->IoStatus.Information);
	if (!NT_SUCCESS(Status)) {
		DbgPrint("[-] failed to enum ips, error: %ld\n", Status);
		Irp->IoStatus.Information = 0;

		return Status;
	}

	return Status;
}
#include "driver.h"


UNICODE_STRING DEVICENAME = RTL_CONSTANT_STRING(L"\\Device\\" DRIVERNAME);
UNICODE_STRING SYMLINKNAME = RTL_CONSTANT_STRING(L"\\DosDevices\\"DRIVERNAME);


NTSTATUS CreateSymLinkDevice(PDRIVER_OBJECT DriverObject, PDEVICE_OBJECT* DeviceObject) {
	//create device object
	NTSTATUS Status = IoCreateDevice(DriverObject, 0, &DEVICENAME, FILE_DEVICE_UNKNOWN, FILE_DEVICE_SECURE_OPEN, FALSE, DeviceObject);
	if (!NT_SUCCESS(Status)) {
		DbgPrint("[-] failed to create a device object in DriverEntry, status: %l\n", Status);
		return Status;
	}


	//create symbolic link
	Status = IoCreateSymbolicLink(&SYMLINKNAME, &DEVICENAME);
	if (!NT_SUCCESS(Status)) {
		DbgPrint("[-] failed to create a symbolic link in DriverEntry, status: %l\n", Status);
		IoDeleteDevice(*DeviceObject);
		return Status;
	}

	return Status;
}


VOID SetMajorFunctions(PDRIVER_OBJECT DriverObject) {
	DriverObject->MajorFunction[IRP_MJ_CREATE] = CreateClose;
	DriverObject->MajorFunction[IRP_MJ_CLOSE] = CreateClose;
	DriverObject->MajorFunction[IRP_MJ_DEVICE_CONTROL] = DeviceIoControl;
	DriverObject->DriverUnload = DriverUnload;
}


VOID DriverUnload(_In_ PDRIVER_OBJECT DriverObject) 
	/*
	driver unload function

	@param DriverObject
	*/
{

	DbgPrint("[+] DriverUnload called on driver!\n");

	PDEVICE_OBJECT DeviceObject = DriverObject->DeviceObject;

	CleanupWfp();
	IoDeleteDevice(DeviceObject);
	IoDeleteSymbolicLink(&SYMLINKNAME);
}


NTSTATUS DeviceIoControl(_Inout_ PDEVICE_OBJECT DeviceObject, _Inout_ PIRP Irp) 
	/*
	device control dispatch function

	@param DeviceObject
	@param Irp
	@return status
	*/
{
	
	NTSTATUS Status = STATUS_SUCCESS;

	DbgPrint("[+] DeviceIoControl called on driver!\n");


	PIO_STACK_LOCATION IoStackLocation = IoGetCurrentIrpStackLocation(Irp);
	ULONG inputBufferLength = IoStackLocation->Parameters.DeviceIoControl.InputBufferLength;
	ULONG outputBufferLength = IoStackLocation->Parameters.DeviceIoControl.OutputBufferLength;
	PVOID inputBuffer;
	PVOID outputBuffer;

	ULONG IoControlCode = IoStackLocation->Parameters.DeviceIoControl.IoControlCode;

	DbgPrint("[+] checking IoControlCode\n");
	switch (IoControlCode) {
		case IOCTL_DRIVER_TEST:
			DbgPrint("[+] IOCTL_DRIVER_TEST used\n");
		

			// for METHOD_BUFFERED input and output buffers are the same
			// SystemBuffer is the size of the bigger one between the two
			// SystemBuffer has the input data in it and will be overriden by output data

			inputBuffer = Irp->AssociatedIrp.SystemBuffer;
			outputBuffer = Irp->AssociatedIrp.SystemBuffer;

			Status = IOCTLDriverTest(Irp, inputBuffer, inputBufferLength, outputBuffer, outputBufferLength);

			break;

		case IOCTL_DRIVER_BLOCK_IP:
			DbgPrint("[+] IOCTL_DRIVER_BLOCK_IP used\n");

			inputBuffer = Irp->AssociatedIrp.SystemBuffer;
			outputBuffer = Irp->AssociatedIrp.SystemBuffer;

			Status = IOCTLDriverBlockIp(Irp, inputBuffer, inputBufferLength, outputBuffer, outputBufferLength, DeviceObject);

			break;

		case IOCTL_DRIVER_UNBLOCK_IP:
			DbgPrint("[+] IOCTL_DRIVER_UNBLOCK_IP used\n");

			inputBuffer = Irp->AssociatedIrp.SystemBuffer;
			outputBuffer = Irp->AssociatedIrp.SystemBuffer;

			Status = IOCTLDriverUnblockIp(Irp, inputBuffer, inputBufferLength, outputBuffer, outputBufferLength, DeviceObject);

			break;

		case IOCTL_DRIVER_BLOCK_PORT:
			DbgPrint("[+] IOCTL_DRIVER_BLOCK_PORT used\n");

			inputBuffer = Irp->AssociatedIrp.SystemBuffer;
			outputBuffer = Irp->AssociatedIrp.SystemBuffer;

			Status = IOCTLDriverBlockPort(Irp, inputBuffer, inputBufferLength, outputBuffer, outputBufferLength, DeviceObject);

			break;

		case IOCTL_DRIVER_UNBLOCK_PORT:
			DbgPrint("[+] IOCTL_DRIVER_UNBLOCK_PORT used\n");

			inputBuffer = Irp->AssociatedIrp.SystemBuffer;
			outputBuffer = Irp->AssociatedIrp.SystemBuffer;

			Status = IOCTLDriverUnblockPort(Irp, inputBuffer, inputBufferLength, outputBuffer, outputBufferLength, DeviceObject);

			break;

		case IOCTL_DRIVER_ENUM_IP:
			DbgPrint("[+] IOCTL_DRIVER_ENUM_IP used\n");

			outputBuffer = Irp->AssociatedIrp.SystemBuffer;

			Status = IOCTLDriverEnumIp(Irp, outputBuffer, outputBufferLength, DeviceObject);

			break;

		case IOCTL_DRIVER_ENUM_PORT:
			DbgPrint("[+] IOCTL_DRIVER_ENUM_PORT used\n");

			outputBuffer = Irp->AssociatedIrp.SystemBuffer;

			Status = IOCTLDriverEnumPort(Irp, outputBuffer, outputBufferLength, DeviceObject);

			break;

		default:
			Status = STATUS_INVALID_DEVICE_REQUEST;
			DbgPrint("[-] invalid IoControlCode: %ul\n", IoControlCode);

			break;
	}

	DbgPrint("-------------\n[+] done, status: %ld\n-------------\n", Status);
	Irp->IoStatus.Status = Status;

	IoCompleteRequest(Irp, IO_NO_INCREMENT);

	DbgPrint("[+] request completed\n");

	return Status;
}


NTSTATUS CreateClose(_Inout_ PDEVICE_OBJECT DeviceObject, _Inout_ PIRP Irp)
	/*
	dispatch function for IRP_MJ_CREATE and IRP_MJ_CLOSE

	@param DeviceObject
	@param Irp
	@return status
	*/
{

	UNREFERENCED_PARAMETER(DeviceObject);

	DbgPrint("[+] CreateClose called on driver!\n");

	Irp->IoStatus.Status = STATUS_SUCCESS;
	Irp->IoStatus.Information = 0;

	IoCompleteRequest(Irp, IO_NO_INCREMENT);

	return STATUS_SUCCESS;
}



NTSTATUS DriverEntry(_In_ PDRIVER_OBJECT DriverObject, _In_ PUNICODE_STRING RegistryPath) 
	/*
	driver entry point
	initializes device object and symbolic link and sets up driver object

	@param DriverObject
	@param RegistryPath
	@return status
	*/
{

	NTSTATUS Status = STATUS_SUCCESS;

	//unreference unused parameters
	UNREFERENCED_PARAMETER(RegistryPath);
	DbgPrint("[+] DriverEntry called on driver!\n");


	//setup device object and symbolic link
	PDEVICE_OBJECT DeviceObject;
	Status = CreateSymLinkDevice(DriverObject, &DeviceObject);
	if (!NT_SUCCESS(Status)) return Status;


	//register major functions
	SetMajorFunctions(DriverObject);


	Status = StartupWfp(DeviceObject);
	if (!NT_SUCCESS(Status)) goto DELETE_DEVICE_SYMLINK;


	return Status;



	//if (!NT_SUCCESS(Status))
DELETE_DEVICE_SYMLINK:

	IoDeleteDevice(DeviceObject);
	IoDeleteSymbolicLink(&SYMLINKNAME);

	return Status;
}
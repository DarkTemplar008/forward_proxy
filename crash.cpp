#include <Windows.h>

#include <iostream>
#include <string>

static void load_debug_privilege(void) {
  const DWORD flags = TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY;
  TOKEN_PRIVILEGES tp;
  HANDLE token;
  LUID val;

  if (!OpenProcessToken(GetCurrentProcess(), flags, &token)) {
    return;
  }

  if (!!LookupPrivilegeValue(NULL, SE_DEBUG_NAME, &val)) {
    tp.PrivilegeCount = 1;
    tp.Privileges[0].Luid = val;
    tp.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED;

    AdjustTokenPrivileges(token, false, &tp, sizeof(tp), NULL, NULL);
  }

  if (!!LookupPrivilegeValue(NULL, SE_INC_BASE_PRIORITY_NAME, &val)) {
    tp.PrivilegeCount = 1;
    tp.Privileges[0].Luid = val;
    tp.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED;

    if (!AdjustTokenPrivileges(token, false, &tp, sizeof(tp), NULL, NULL)) {
    }
  }

  CloseHandle(token);
}

static inline bool is_64bit_windows(void) {
#ifdef _WIN64
    return true;
#else
  BOOL x86 = false;
  bool success = !!IsWow64Process(GetCurrentProcess(), &x86);
  return success && !!x86;
#endif
}

static inline bool is_64bit_process(HANDLE process) {
  BOOL x86 = true;
  if (is_64bit_windows()) {
    bool success = !!IsWow64Process(process, &x86);
    if (!success) {
      return false;
    }
  }

  return !x86;
}

static inline HANDLE open_target_process(DWORD pid) {
  HANDLE target_process = OpenProcess(PROCESS_ALL_ACCESS, false, pid);
  return target_process;
}

static void remote_exec(void) {
  __debugbreak();
}

static void inject_process(HANDLE target_process) {
  int size = 1024;
  void* mem = VirtualAllocEx(target_process, NULL, size,
                             MEM_RESERVE | MEM_COMMIT, PAGE_EXECUTE_READWRITE);
  if (!mem) {
    return;
  }

  SIZE_T written_size = 0;
  BOOL success =
      WriteProcessMemory(target_process, mem, remote_exec, size, &written_size);
  if (!success) {
    return;
  }

  DWORD thread_id = 0;
  HANDLE thread = CreateRemoteThread(
      target_process, NULL, 0, (LPTHREAD_START_ROUTINE)mem, NULL, 0, &thread_id);
  if (!thread) {
    return;
  }

  if (WaitForSingleObject(thread, INFINITE) == WAIT_OBJECT_0) {
  }

  VirtualFreeEx(target_process, mem, 0, MEM_RELEASE);
  CloseHandle(thread);
}

int main(int argc, char** argv) {
  if (argc < 2) {
    std::cout << "crash.exe <pid>" << std::endl;
    return 0;
  }

  int pid = std::stoi(argv[1]);
  if (pid == 0) {
    std::cout << "invalid pid" << std::endl;
    return 0;
  }

  load_debug_privilege();

  HANDLE target_process = open_target_process(pid);
  bool is_self_x64 = sizeof(void*) == 8;
  bool is_target_x64 = is_64bit_process(target_process);
  if (is_self_x64 != is_target_x64) {
    char cmd[64];
    sprintf(cmd, "crash%d.exe %d", is_target_x64 ? 64 : 32, pid);
    system(cmd);
    return 0;
  }

  inject_process(target_process);

  return 0;
}
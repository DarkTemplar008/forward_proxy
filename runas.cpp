#include <Windows.h>
#include <shellapi.h>

#include <iostream>

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cout << "" << std::endl;
        return 0;
    }

    SHELLEXECUTEINFOA sei;
	ZeroMemory(&sei, sizeof(SHELLEXECUTEINFOA));
	sei.cbSize = sizeof(sei);
	sei.lpFile = argv[1];
	sei.lpVerb = "runas";
	sei.nShow = SW_SHOW;
    std::string param;
    if (argc > 2) {
        for (int i = 2; i < argc; ++i) {
            param += argv[i];
            param += " ";
        }
        sei.lpParameters = param.c_str();
    }
	ShellExecuteExA(&sei);
    return 0;
}
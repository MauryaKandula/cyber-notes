// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Kandula Paul Saketh Maurya (@MauryaKandula)
// Native Windows GUI Executable Host for CyberNotes (`CyberNotes.exe`)
// Hosts the embedded CPython 3.14 runtime (`python314.dll`) in-process so that
// Windows Task Manager, Taskbar, Startup Apps, and Alt+Tab identify the process
// strictly as `CyberNotes.exe` ("CyberNotes — Modern Neon Sticky Notes") with
// zero `python.exe` or `pythonw.exe` process names.

using System;
using System.IO;
using System.Reflection;
using System.Runtime.InteropServices;

[assembly: AssemblyTitle("CyberNotes")]
[assembly: AssemblyDescription("CyberNotes — Modern Neon Sticky Notes for Windows")]
[assembly: AssemblyConfiguration("Release")]
[assembly: AssemblyCompany("Kandula Paul Saketh Maurya (@MauryaKandula)")]
[assembly: AssemblyProduct("CyberNotes")]
[assembly: AssemblyCopyright("Copyright © 2026 Kandula Paul Saketh Maurya. Licensed under MIT.")]
[assembly: AssemblyTrademark("CyberNotes")]
[assembly: AssemblyVersion("2.1.0.0")]
[assembly: AssemblyFileVersion("2.1.0.0")]

namespace CyberNotesHost
{
    internal static class NativeMethods
    {
        [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
        public static extern bool SetDllDirectoryW(string lpPathName);

        [DllImport("shell32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
        public static extern int SetCurrentProcessExplicitAppUserModelID(string AppID);

        [DllImport(@"C:\Python\python314.dll", CallingConvention = CallingConvention.Cdecl, CharSet = CharSet.Unicode)]
        public static extern int Py_Main(int argc, string[] argv);
    }

    internal static class Program
    {
        [STAThread]
        private static int Main(string[] args)
        {
            try
            {
                NativeMethods.SetCurrentProcessExplicitAppUserModelID("MauryaKandula.CyberNotes.Desktop.2.1");
                NativeMethods.SetDllDirectoryW(@"C:\Python");

                string currentPath = Environment.GetEnvironmentVariable("PATH") ?? "";
                if (!currentPath.Contains(@"C:\Python"))
                {
                    Environment.SetEnvironmentVariable("PATH", @"C:\Python;C:\Python\Scripts;" + currentPath);
                }
                Environment.SetEnvironmentVariable("PYTHONHOME", @"C:\Python");
                Environment.SetEnvironmentVariable("PYTHONDONTWRITEBYTECODE", "1");

                string exeDir = AppDomain.CurrentDomain.BaseDirectory.TrimEnd('\\', '/');
                string scriptPath = Path.Combine(exeDir, "cyber_notes.py");
                if (!File.Exists(scriptPath))
                {
                    scriptPath = @"s:\Work\AntiGravity\cyber_notes\cyber_notes.py";
                }

                string[] pyArgv = new string[args.Length + 2];
                pyArgv[0] = Path.Combine(exeDir, "CyberNotes.exe");
                pyArgv[1] = scriptPath;
                for (int i = 0; i < args.Length; i++)
                {
                    pyArgv[i + 2] = args[i];
                }

                return NativeMethods.Py_Main(pyArgv.Length, pyArgv);
            }
            catch (Exception ex)
            {
                try
                {
                    string logPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "host_crash.log");
                    File.WriteAllText(logPath, ex.ToString());
                }
                catch { }
                return 1;
            }
        }
    }
}

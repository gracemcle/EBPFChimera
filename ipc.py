#!/usr/bin/python
# IPC - Instructions Per Cycles using Perf Events and
# uprobes
# 24-Apr-2020	Saleem Ahmad	Created this.

from bcc import BPF, utils
from optparse import OptionParser

# load BPF program
code="""
#include <uapi/linux/ptrace.h>

struct perf_delta {
    u64 clk_delta;
    u64 inst_delta;
    u64 time_delta;
};

/*

perf event: tool for event-oriented observability to answer questions like
What reasons are threads leaving the CPU?, 
Is a certain kernel function being called, and how often?
Which code-paths are causing CPU level 2 cache misses?

*/

BPF_PERF_ARRAY(clk, MAX_CPUS);
BPF_PERF_ARRAY(inst, MAX_CPUS);

BPF_PERF_OUTPUT(output);

/*
Per-CPU variables are variables which each processor will have its own copy of the variable
*/

BPF_PERCPU_ARRAY(data, u64);

#define CLOCK_ID 0
#define INSTRUCTION_ID 1
#define TIME_ID 2

/* pt_regs: a struct that represents the CPU register state
    at the time of an interrupt, exception, or sys call.
    usually used to capture state of registers when switching
    between user mode and kernel mode
*/

void trace_start(struct pt_regs *ctx){

    u32 clk_k = CLOCK_ID;
    u32 inst_k = INSTRUCTION_ID;
    u32 time = TIME_ID;

    // what is bpf_get_smp_processor_id?

    int cpu = bpf_get_smp_processor_id();

    u64 clk_start = clk.perf_read(cpu);
    u64 inst_start = inst.perf_read(cpu);
    u64 time_start = bpf_ktime_get_ns();

    u64* kptr = NULL;
    kptr = data.lookup(&clk_k);
    if(kptr){
        data.update(&clk_k, &clk_start);
    }
    else{
        data.insert(&clk_k, &clk_start);
    }

    kptr = data.lookup(&inst_k);

    if(kptr){
        data.update(&time, &time_start);
    }else{
        data.insert(&time, &time_start);
    }
}

void trace_end(struct pt_regs* ctx){
    u32 clk_k = CLOCK_ID;
    u32 inst_k = INSTRUCTION_ID;
    u32 time = TIME_ID;

    int cpu = bpf_get_smp_processor_id();

    u64 clk_end = clk.perf_read(cpu);
    u64 inst_end = inst.perf_read(cpu);
    u64 time_end = bpf_ktime_get_ns();
    
    struct perf_delta perf_data = {} ;
    u64* kptr = NULL;
    kptr = data.lookup(&clk_k);

    // Find elements in map, if not found return
    if (kptr) {
        perf_data.clk_delta = clk_end - *kptr;
    } else {
        return;
    }
    
    kptr = data.lookup(&inst_k);
    if (kptr) {
        perf_data.inst_delta = inst_end - *kptr;
    } else {
        return;
    }

    kptr = data.lookup(&time);
    if (kptr) {
        perf_data.time_delta = time_end - *kptr;
    } else {
        return;
    }

    output.perf_submit(ctx, &perf_data, sizeof(struct perf_delta));
}
"""

usage = 'Usage: ipc.py [options]\n./ipc.py -l c -s strlen'
parser = OptionParser(usage)
parser.add_option('-l', '--lib', dest='lib_name', help='lib name containing symbol to trace, e.g. c for libc', type=str)
parser.add_option('-s', '--sym', dest='sym', help='symbol to trace', type=str)

(options, args) = parser.parse_args()
if(not options.lib_name or not options.sym):
    parser.print_help()
    exit()

num_cpus = len(utils.get_online_cpus())

b = BPF(text=code, cflags=['-DMAX_CPUS=%s' % str(num_cpus)])

b.attach_uprobe(name=options.lib_name, sym=options.sym, fn_name="trace_start")
b.attach_uretprobe(name=options.lib_name, sym=options.sym, fn_name="trace_end")

def print_data(cpu, data, size):
    e = b["output"].event(data)
    print("%-8d %-12d %-8.2f %-8s %d" % (e.clk_delta, e.inst_delta, 
        1.0* e.inst_delta/e.clk_delta, str(round(e.time_delta * 1e-3, 2)) + ' us', cpu))

print("Counters Data")
print("%-8s %-12s %-8s %-8s %s" % ('CLOCK', 'INSTRUCTION', 'IPC', 'TIME', 'CPU'))

b["output"].open_perf_buffer(print_data)

PERF_TYPE_HARDWARE = 0
PERF_COUNT_HW_CPU_CYCLES = 0
PERF_COUNT_HW_INSTRUCTIONS = 1
# Unhalted Clock Cycles
b["clk"].open_perf_event(PERF_TYPE_HARDWARE, PERF_COUNT_HW_CPU_CYCLES)
# Instruction Retired
b["inst"].open_perf_event(PERF_TYPE_HARDWARE, PERF_COUNT_HW_INSTRUCTIONS)

while True:
    try:
        b.perf_buffer_poll()
    except KeyboardInterrupt:
        exit()

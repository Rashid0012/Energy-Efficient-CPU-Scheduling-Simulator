import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from typing import List, Dict
import random

class Process:
    def __init__(self, pid: int, arrival_time: int, burst_time: int, priority: int):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.priority = priority
        self.waiting_time = 0
        self.turnaround_time = 0
        self.energy_consumed = 0

class EnergyEfficientScheduler:
    def __init__(self, processes: List[Process], time_quantum: int = 2):
        self.processes = processes
        self.time_quantum = time_quantum
        self.current_time = 0
        self.completed_processes = []
        self.energy_consumption = 0
        self.idle_time = 0

    def calculate_energy(self, time_slice: int, is_idle: bool = False) -> float:
        # Energy consumption model
        if is_idle:
            return time_slice * 0.1  # Lower energy consumption during idle
        return time_slice * 0.5  # Higher energy consumption during execution

    def run_simulation(self):
        ready_queue = []
        current_process = None
        time_slice_remaining = 0

        while len(self.completed_processes) < len(self.processes):
            # Add newly arrived processes
            for p in self.processes:
                if p.arrival_time == self.current_time and p not in ready_queue and p not in self.completed_processes:
                    ready_queue.append(p)

            if current_process is None and ready_queue:
                current_process = ready_queue.pop(0)
                time_slice_remaining = self.time_quantum

            if current_process:
                # Execute process
                execution_time = min(time_slice_remaining, current_process.remaining_time)
                current_process.remaining_time -= execution_time
                self.energy_consumption += self.calculate_energy(execution_time)
                time_slice_remaining -= execution_time

                if current_process.remaining_time == 0:
                    current_process.turnaround_time = self.current_time + execution_time - current_process.arrival_time
                    current_process.waiting_time = current_process.turnaround_time - current_process.burst_time
                    self.completed_processes.append(current_process)
                    current_process = None
                elif time_slice_remaining == 0:
                    ready_queue.append(current_process)
                    current_process = None
            else:
                # CPU is idle
                self.idle_time += 1
                self.energy_consumption += self.calculate_energy(1, True)

            self.current_time += 1

def generate_random_processes(num_processes: int) -> List[Process]:
    processes = []
    for i in range(num_processes):
        arrival_time = random.randint(0, 10)
        burst_time = random.randint(1, 10)
        priority = random.randint(1, 5)
        processes.append(Process(i, arrival_time, burst_time, priority))
    return processes

def plot_results(scheduler: EnergyEfficientScheduler):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
    
    # Plot waiting times
    waiting_times = [p.waiting_time for p in scheduler.completed_processes]
    ax1.bar(range(len(waiting_times)), waiting_times)
    ax1.set_title('Process Waiting Times')
    ax1.set_xlabel('Process ID')
    ax1.set_ylabel('Waiting Time')
    
    # Plot energy consumption
    energy_data = {
        'Execution': scheduler.energy_consumption - (scheduler.idle_time * 0.1),
        'Idle': scheduler.idle_time * 0.1
    }
    ax2.pie(energy_data.values(), labels=energy_data.keys(), autopct='%1.1f%%')
    ax2.set_title('Energy Consumption Distribution')
    
    return fig

def main():
    st.title("Energy-Efficient CPU Scheduling Simulation")
    
    st.sidebar.header("Simulation Parameters")
    num_processes = st.sidebar.slider("Number of Processes", 3, 10, 5)
    time_quantum = st.sidebar.slider("Time Quantum", 1, 5, 2)
    
    if st.sidebar.button("Generate New Processes"):
        processes = generate_random_processes(num_processes)
        scheduler = EnergyEfficientScheduler(processes, time_quantum)
        scheduler.run_simulation()
        
        # Display process details
        st.subheader("Process Details")
        process_data = []
        for p in scheduler.completed_processes:
            process_data.append({
                'PID': p.pid,
                'Arrival Time': p.arrival_time,
                'Burst Time': p.burst_time,
                'Priority': p.priority,
                'Waiting Time': p.waiting_time,
                'Turnaround Time': p.turnaround_time
            })
        st.dataframe(pd.DataFrame(process_data))
        
        # Display statistics
        st.subheader("Performance Metrics")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average Waiting Time", 
                     f"{sum(p.waiting_time for p in scheduler.completed_processes)/len(scheduler.completed_processes):.2f}")
        with col2:
            st.metric("Total Energy Consumption", f"{scheduler.energy_consumption:.2f}")
        with col3:
            st.metric("CPU Utilization", 
                     f"{(1 - scheduler.idle_time/scheduler.current_time)*100:.2f}%")
        
        # Plot results
        st.subheader("Visualization")
        fig = plot_results(scheduler)
        st.pyplot(fig)

if __name__ == "__main__":
    main() 
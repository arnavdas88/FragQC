OPENQASM 2.0;
include "qelib1.inc";

qreg q[5];
creg c[5];

h q[0];
h q[1];
h q[2];
h q[3];
h q[4];

rz(-0.4) q[0];
rz(-0.4) q[1];
rz(-0.4) q[2];
rz(-0.4) q[3];
rz(-0.4) q[4];

// Main QAOA Circuit
// Part - 01

cx q[1], q[2]; // cx0
cx q[0], q[3]; // cx2

rz(0.1) q[3];
rz(0.2) q[2];

cx q[1], q[2]; // cx1
cx q[0], q[3]; // cx3

rz(-0.4) q[1];
rz(-0.4) q[2];
rz(-0.4) q[3];

cx q[1], q[3]; // cx4
cx q[2], q[4]; // cx6

rz(0.4) q[3];
rz(0.4) q[4];

cx q[1], q[3]; // cx5
cx q[2], q[4]; // cx7

rx(5.15) q[0];
rx(5.15) q[1];
rx(5.15) q[2];
rx(5.15) q[3];
rx(5.15) q[4];

measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
measure q[3] -> c[3];
measure q[4] -> c[4];

OPENQASM 2.0;
include "qelib1.inc";

qreg q[4];
creg c[4];


// Rep 1

ry(0.8) q[0];
ry(0.8) q[1];
ry(0.8) q[2];
ry(0.8) q[3];

rz(0.8) q[0];
rz(0.8) q[1];
rz(0.8) q[2];
rz(0.8) q[3];

cx q[0], q[1]; // cx0
cx q[1], q[2]; // cx1
cx q[2], q[3]; // cx2

// Rep 2

ry(0.8) q[0];
ry(0.8) q[1];
ry(0.8) q[2];
ry(0.8) q[3];

rz(0.8) q[0];
rz(0.8) q[1];
rz(0.8) q[2];
rz(0.8) q[3];

cx q[0], q[1]; // cx0
cx q[1], q[2]; // cx1
cx q[2], q[3]; // cx2

// Rep 3

ry(0.8) q[0];
ry(0.8) q[1];
ry(0.8) q[2];
ry(0.8) q[3];

rz(0.8) q[0];
rz(0.8) q[1];
rz(0.8) q[2];
rz(0.8) q[3];

cx q[0], q[1]; // cx0
cx q[1], q[2]; // cx1
cx q[2], q[3]; // cx2


measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
measure q[3] -> c[3];

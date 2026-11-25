#!/usr/bin/env python3
"""Numerically verify the worked circuit calculations (requires NumPy)."""
import numpy as np
from itertools import product
I=np.eye(2);H=np.array([[1,1],[1,-1]])/np.sqrt(2);X=np.array([[0,1],[1,0]]);Z=np.diag([1,-1]);zero=np.array([1,0]);one=np.array([0,1])
def close(a,b):assert np.allclose(a,b,atol=1e-10),(a,b)
def cx(n,c,t):
 m=np.zeros((2**n,2**n))
 for x in range(2**n):m[x^(1<<(n-1-t)) if x&(1<<(n-1-c)) else x,x]=1
 return m
def local(n,q,u):
 a=np.array([1.])
 for i in range(n):a=np.kron(a,u if q==i else I)
 return a
close(H@H,I)
for a,b in product([0,1],repeat=2):
 nand=lambda x,y:1-x*y
 t=nand(a,b);u=nand(a,t);v=nand(b,t)
 assert nand(u,v)==a^b
close(cx(2,0,1)@np.kron(H,I)@np.kron(zero,zero),np.array([1,0,0,1])/np.sqrt(2))
# Every computational output in the illustrated four-item circuit.
cz=np.diag([1,1,1,-1]);hh=np.kron(H,H);xx=np.kron(X,X)
s=np.ones(4)/2;D=2*np.outer(s,s)-np.eye(4)
close(hh@xx@cz@xx@hh,-D)
close(abs(hh@xx@cz@xx@hh@cz@s)**2,[0,0,0,1])
# The geometric reading of section 8.1.3: the overlap with |s⟩ fixes the angle
# to the mirror, and D maps each amplitude to twice the mean minus itself.
zero2=np.eye(4)[:,0]
close(abs(np.vdot(s,zero2)),.5)
close(np.arccos(abs(np.vdot(s,zero2))),np.pi/3)
close(D@zero2,s-zero2)
close(D@zero2,[-.5,.5,.5,.5])
amps=np.array([.3,-.4j,.5,.2+.1j])
close(D@amps,2*amps.mean()-amps)
# All four function oracles for Deutsch.
for f in product([0,1],repeat=2):
 u=np.zeros((4,4))
 for x,y in product([0,1],repeat=2):u[2*x+(y^f[x]),2*x+y]=1
 out=np.kron(H,I)@u@hh@np.kron(zero,one)
 close([sum(abs(out[:2])**2),sum(abs(out[2:])**2)],[1,0] if f[0]==f[1] else [0,1])
# Teleportation with complex amplitudes: all four conditioned corrections.
psi=np.array([np.sqrt(.3),np.exp(.73j)*np.sqrt(.7)])
bell=np.array([1,0,0,1])/np.sqrt(2)
out=local(3,0,H)@cx(3,0,1)@np.kron(psi,bell)
for m,n in product([0,1],repeat=2):
 branch=out[2*(2*m+n):2*(2*m+n)+2]
 close(np.linalg.norm(branch)**2,.25)
 close(np.linalg.matrix_power(Z,m)@np.linalg.matrix_power(X,n)@branch*2,psi)
# General amplification agrees with the two-dimensional formula for all steps.
for N in [4,8,16]:
 for M in range(1,N):
  s=np.ones(N)/np.sqrt(N);o=np.diag([-1]*M+[1]*(N-M));d=2*np.outer(s,s)-np.eye(N);v=s.copy();theta=np.arcsin(np.sqrt(M/N))
  for k in range(8):
   close(sum(abs(v[:M])**2),np.sin((2*k+1)*theta)**2);v=d@o@v
print('Verified NAND XOR, H², Bell preparation, diffusion, four Deutsch oracles, all teleportation outcomes, and amplification probabilities.')

# The complex square root of NOT preserves norm as well as squaring to X.
root_x=np.array([[1+1j,1-1j],[1-1j,1+1j]])/2
close(root_x@root_x,X)
close(root_x.conj().T@root_x,I)
# Coarse measurement preserves coherence inside a degenerate eigenspace.
v=np.ones(3)/np.sqrt(3);p0=np.diag([1,1,0]);coherent=p0@v/np.sqrt(2/3)
plus3=np.array([1,1,0])/np.sqrt(2)
close(np.linalg.norm(p0@v)**2,2/3)
close(abs(np.vdot(plus3,coherent))**2,1)
close(plus3@np.diag([.5,.5,0])@plus3,.5)
# Ignoring Alice's outcome gives the same local state in either basis.
plus=(zero+one)/np.sqrt(2);minus=(zero-one)/np.sqrt(2)
close((np.outer(plus,plus)+np.outer(minus,minus))/2,I/2)
# The wrong kickback target remains unchanged and conveys no function value.
for f in product([0,1],repeat=2):
 u=np.zeros((4,4))
 for x,y in product([0,1],repeat=2):u[2*x+(y^f[x]),2*x+y]=1
 close(u@np.kron(plus,plus),np.kron(plus,plus))
# Appendix D: effects are positive, complete, and never give a false conclusive result.
c=1/(1+1/np.sqrt(2));e0=c*np.outer(minus,minus);ep=c*np.outer(one,one);eq=I-e0-ep
assert np.linalg.eigvalsh(eq).min()>-1e-10
close(plus@e0@plus,0);close(zero@ep@zero,0)
print('Verified square root of NOT, coarse measurement, local ensembles, wrong-target kickback, and inconclusive discrimination.')

# Rotated measurement bases: completeness, Born probabilities, and repeatability.
for alpha in np.linspace(-np.pi/2,np.pi/2,19):
 psi=np.array([np.cos(alpha),np.sin(alpha)])
 for beta in np.linspace(0,np.pi/2,19):
  basis=np.array([[np.cos(beta),-np.sin(beta)],[np.sin(beta),np.cos(beta)]])
  close(basis.T@basis,I)
  projectors=[np.outer(basis[:,j],basis[:,j]) for j in range(2)]
  close(sum(projectors),I)
  probabilities=np.array([np.linalg.norm(p@psi)**2 for p in projectors])
  close(probabilities,[np.cos(alpha-beta)**2,np.sin(alpha-beta)**2])
  for j,p in enumerate(projectors):
   if probabilities[j]>1e-12:
    collapsed=p@psi/np.sqrt(probabilities[j])
    close(np.linalg.norm(collapsed),1)
    close(np.linalg.norm(p@collapsed)**2,1)
plus=(zero+one)/np.sqrt(2);minus=(zero-one)/np.sqrt(2)
close(abs(H@plus)**2,[1,0]);close(abs(H@minus)**2,[0,1])
print('Verified rotated-basis measurement probabilities, completeness, and conditional repeatability.')
# Chapter 8: conjugation, controlled phases, controlled-U, two controls from one, SWAP, two-level pieces, bit-flip code.
def ctrl(n,cs,t,U):
 N=2**n;m=np.zeros((N,N),complex)
 for x in range(N):
  bits=[(x>>(n-1-w))&1 for w in range(n)]
  if all(bits[c] for c in cs):
   for y in range(2):
    b2=bits[:];b2[t]=y;m[sum(b<<(n-1-w) for w,b in enumerate(b2)),x]+=U[y,bits[t]]
  else:m[x,x]=1
 return m
def op(n,gates):
 m=np.array([[1.]])
 for w in range(n):m=np.kron(m,gates.get(w,I))
 return m
R=lambda t:np.diag([1,np.exp(1j*t)]);S=R(np.pi/2);T=R(np.pi/4)
close(H@X@H,Z);close(op(2,{1:H})@cx(2,0,1)@op(2,{1:H}),cz)
close(op(2,{0:X})@cz@op(2,{0:X}),np.diag([1,-1,1,1]))
close(S@S,Z);close(T@T,S);close(np.linalg.matrix_power(T,8),I)
def cphase(n,c,t,phi):return cx(n,c,t)@op(n,{t:R(-phi/2)})@cx(n,c,t)@op(n,{c:R(phi/2),t:R(phi/2)})
for phi in np.linspace(-np.pi,np.pi,9):close(cphase(2,0,1,phi),np.diag([1,1,1,np.exp(1j*phi)]))
rng=np.random.default_rng(8)
for _ in range(25):
 U,_r=np.linalg.qr(rng.normal(size=(2,2))+1j*rng.normal(size=(2,2)));lam,W=np.linalg.eig(U);W,_r=np.linalg.qr(W);lam=np.diag(W.conj().T@U@W);a,b=np.angle(lam)
 close(op(2,{1:W})@ctrl(2,[0],1,R(b-a))@op(2,{0:R(a)})@op(2,{1:W.conj().T}),ctrl(2,[0],1,U))
 V=W@np.diag(np.sqrt(lam))@W.conj().T
 close(ctrl(3,[0],2,V)@cx(3,0,1)@ctrl(3,[1],2,V.conj().T)@cx(3,0,1)@ctrl(3,[1],2,V),ctrl(3,[0,1],2,U))
ccz=cphase(3,0,2,np.pi/2)@cx(3,0,1)@cphase(3,1,2,-np.pi/2)@cx(3,0,1)@cphase(3,1,2,np.pi/2)
close(ccz,np.diag([1]*7+[-1]));close(op(3,{2:H})@ccz@op(3,{2:H}),ctrl(3,[0,1],2,X))
close(cx(2,0,1)@cx(2,1,0)@cx(2,0,1),np.eye(4)[[0,2,1,3]])
close(ctrl(2,[1],0,H)@op(2,{1:X})@ctrl(2,[1],0,H)@op(2,{1:X}),np.kron(H,I))
p,q=0.6,0.8j;r=np.hypot(abs(p),abs(q));G=np.array([[np.conj(p),np.conj(q)],[-q,p]])/r;close(G@G.conj().T,I);close(G@np.array([p,q]),[r,0])
amp=np.zeros(8,complex);amp[0],amp[7]=0.6,0.8;theta=0.4
hit=op(3,{1:np.cos(theta/2)*I-1j*np.sin(theta/2)*X})@amp
syn=lambda x:(((x>>2)^(x>>1))&1,((x>>1)^x)&1)
p00=sum(abs(hit[x])**2 for x in range(8) if syn(x)==(0,0));p11=sum(abs(hit[x])**2 for x in range(8) if syn(x)==(1,1))
close([p00,p11],[np.cos(theta/2)**2,np.sin(theta/2)**2])
print('Verified Chapter 8 constructions: controlled-Z, marking, controlled phases, controlled-U, two controls from one, Toffoli from CNOT, H and T, SWAP, two-level pieces, and syndrome probabilities.')

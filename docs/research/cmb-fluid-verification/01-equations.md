# Governing equations

The experiment uses a deliberately reduced conservation-law model to make every assumption visible.

## State

```text
rho = rho0
u = 0
v = 0
w = 0
p(x,t) = cos(k*x - omega*t)
E = E0
```

The pressure field varies in space and time while the velocity field is constrained to zero.

## Residual form

For the reduced one-dimensional demonstration:

```text
R_mass = d(rho)/dt + d(rho*u)/dx

R_momentum = d(rho*u)/dt
           + d(rho*u^2)/dx
           + dp/dx
           - f_x

R_energy = dE/dt
         + d(u*E)/dx
         + d(u*p)/dx
```

Under `u = 0`, constant `rho`, and constant `E`:

```text
R_mass = 0
R_energy = 0
R_momentum = dp/dx - f_x
```

For

```text
theta = k*x - omega*t
p = cos(theta)
```

SymPy gives

```text
dp/dx = -k*sin(theta)
```

Choosing

```text
f_x = dp/dx
```

therefore yields

```text
R_momentum = 0
```

## Sign convention

The reference implementation writes momentum balance as

```text
... + dp/dx - f_x = 0
```

so the balancing term is `f_x = dp/dx`. A conventional force-density equation may place the pressure-gradient term on the opposite side and use `f_x = -dp/dx`. The physics is the same once the sign convention is stated consistently.

## Scope

This is an exact solution of the stated reduced forced model. It is not a general solution of the full nonlinear three-dimensional Navier-Stokes initial-boundary-value problem.

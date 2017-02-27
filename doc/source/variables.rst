Variables in LADIM
==================

To obtain the necessary flexibility of different IBMs and different
gridforce module determined by at run time by the configuration, it
is necessary to have a strict terminology for variables.

First some basics, a ``particle`` is the fundamental entity of particle
tracking. It has positions and possibly other attributes and keeps its identity
troughout the simulation. A ``particle instance`` or simply an ``instance`` is
a particle at a fixed time. The ``pid``, short for particle identifier, maps
a particle instance to its particle.

Particle variable
  A variable associated to a particle, that does not depend on time.

Particle instance variable
  A variable associated to a particle instance. Typically time-dependent.

Position variables
  Instance variables, X, Y, and Z, that gives the position of the instance
  in grid coordinates.

Particle identifier
  The projection, ``pid`` from particle instance to particle. It is considered
  an instance variable.

Mandatory variables
  The position variables and the particle identifier

State variables
  The total collection of variables that determine the model state.

IBM-variable
  A non-mandatory state variable.

Derived variables
  Variables such as longitude and latitude, derived from the state variables.

Forcing variable
  A variable from the forcing file that is used to modify the model state.
  Main examples are the mandatory horizontal velocity components U and V.
  Non-mandatory forcing variables, for instance temperature, are called
  IBM forcing variables.

Release variable
  A variable read from the particle release file, such as initial position.

Output variable
  A variable that is written to the output file


Some particle variables, for instance location number, has no influence on the
dynamics and are simply written to output for extra information. Other particle
variables may store initial information, like release time or release position,
and has no further influence. Other particle variables may influence the
dynamics throughout  the simulation. Examples are diameter or sinking velovity
of non-organic sediment particles. The last category are counted as
IBM-variables.

Some variables have predefined names. For the state these are the position
variables, ``X``, ``Y``, ``Z`` and the particle identifier ``pid``.  Similarly,
the derived longitude and latitude have names ``lon`` and ``lat``  respectively.
For the forcing variables it is the horizontal velocity components ``U`` and
``V`` in the grid directions. IBM variables are referenced indirectly like
state.temp or state[name] where state is a State object.

The particle identifier, ``pid`` is per definition a particle variable. However,
it "lives" on particle instances, identifying the particle the instance belongs to.
It is therefore considered an instance variable.

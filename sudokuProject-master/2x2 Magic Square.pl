% suggested query: main.

:- use_module(library(clpfd)).

main :-
	solutions
	;
	halt.

main2 :-
	solutions
	;
	fail.

solutions :-
	statistics(runtime,_),
	fd_statistics(backtracks,_),
	write('=========================[ Solutions ]========================='),
	nl,
	(	the_problem(__S),
		write('[A,B,C,D] = '), write(__S),
		nl,
		fail
	;
		write('=======================[ End Solutions ]======================='),
		nl,
		fail
	).

the_problem([A,B,C,D]) :-
	A in 1..4,
	B in 1..4,
	C in 1..4,
	D in 1..4,
	all_constraints([A,B,C,D]),
	labeling([leftmost, step, up], [A,B,C,D]),
	fd_statistics(backtracks,__BT),
	write('Backtracks: '), write(__BT), nl,
	statistics(runtime,[_,__RT]),
	__RTsec is __RT / 1000,
	write('Runtime: '), write(__RTsec), write('s'), nl.

find_var([(V,N)|_], N, V) :- !.
find_var([_|Vs], N, V) :-
	find_var(Vs, N, V).

all_constraints([A,B,C,D]) :-
	write('Adding constraint "'), write('A+B=4"'), write(' for values:'), nl,
	the_constraint1(A,B),
	write('Adding constraint "'), write('A+C=4"'), write(' for values:'), nl,
	the_constraint2(A,C),
	write('Adding constraint "'), write('A+D=4"'), write(' for values:'), nl,
	the_constraint3(A,D),
	write('Adding constraint "'), write('B+C=4"'), write(' for values:'), nl,
	the_constraint4(B,C),
	write('Adding constraint "'), write('B+D=4"'), write(' for values:'), nl,
	the_constraint5(B,D),
	write('Adding constraint "'), write('C+D=4"'), write(' for values:'), nl,
	the_constraint6(C,D),
	write('Adding constraint "'), write('A \\= B"'), write(' for values:'), nl,
	the_constraint7(A,B),
	write('Adding constraint "'), write('A\\=D"'), write(' for values:'), nl,
	the_constraint8(A,D),
	write('Adding constraint "'), write('A\\=C"'), write(' for values:'), nl,
	the_constraint9(A,C),
	write('Adding constraint "'), write('B\\=C"'), write(' for values:'), nl,
	the_constraint10(B,C),
	write('Adding constraint "'), write('C\\=D"'), write(' for values:'), nl,
	the_constraint11(C,D),
	write('Adding constraint "'), write('B\\=D"'), write(' for values:'), nl,
	the_constraint12(B,D).

the_constraint1(A, B) :- !,
	A+B#=4.
the_constraint1(_,_).

the_constraint2(A, C) :- !,
	A+C#=4.
the_constraint2(_,_).

the_constraint3(A, D) :- !,
	A+D#=4.
the_constraint3(_,_).

the_constraint4(B, C) :- !,
	B+C#=4.
the_constraint4(_,_).

the_constraint5(B, D) :- !,
	B+D#=4.
the_constraint5(_,_).

the_constraint6(C, D) :- !,
	C+D#=4.
the_constraint6(_,_).

the_constraint7(A, B) :- !,
	A #\= B.
the_constraint7(_,_).

the_constraint8(A, D) :- !,
	A#\=D.
the_constraint8(_,_).

the_constraint9(A, C) :- !,
	A#\=C.
the_constraint9(_,_).

the_constraint10(B, C) :- !,
	B#\=C.
the_constraint10(_,_).

the_constraint11(C, D) :- !,
	C#\=D.
the_constraint11(_,_).

the_constraint12(B, D) :- !,
	B#\=D.
the_constraint12(_,_).


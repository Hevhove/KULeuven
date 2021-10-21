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
		write('[X] = '), write(__S),
		nl,
		fail
	;
		write('=======================[ End Solutions ]======================='),
		nl,
		fail
	).

the_problem([X]) :-
	length(X,81),
	domain(X,1,9),
	numbered_list(X,XL,0),
	all_constraints([XL]),
	myappend([],X,__Tmp1),
	labeling([leftmost, step, up], __Tmp1),
	fd_statistics(backtracks,__BT),
	write('Backtracks: '), write(__BT), nl,
	statistics(runtime,[_,__RT]),
	__RTsec is __RT / 1000,
	write('Runtime: '), write(__RTsec), write('s'), nl.

find_var([(V,N)|_], N, V) :- !.
find_var([_|Vs], N, V) :-
	find_var(Vs, N, V).

numbered_list([X],[(X,Acc)],Acc) :- !.
numbered_list([X|Xs],[(X,Acc)|XNs],Acc) :-
	Acc1 is Acc + 1,
	numbered_list(Xs,XNs,Acc1).

myappend([],L,L).
myappend([X|L1],L2,[X|L12]) :-
	myappend(L1,L2,L12).

all_constraints([X]) :-
	write('Adding constraint "'), write('X_I \\= X_J"'), write(' for values:'), nl,
	the_constraint1(X,X),
	write('Adding constraint "'), write('X_I \\= X_J"'), write(' for values:'), nl,
	the_constraint2(X,X),
	write('Adding constraint "'), write('X_I \\= X_J"'), write(' for values:'), nl,
	the_constraint3(X,X),
	write('Adding constraint "'), write('X_I = X_J => X_I=X_H \\/ X_Hp1 = X_I \\/ X_Hp2 = X_I"'), write(' for values:'), nl,
	the_constraint4(X,X,X,X,X),
	write('Adding constraint "'), write('X_I = X_J => X_I=X_H \\/ X_Hp9 = X_I \\/ X_Hp18 = X_I"'), write(' for values:'), nl,
	the_constraint5(X,X,X,X,X),
sudoku(X).

the_constraint1([],_).
the_constraint1([X_I|X_Is],X_J) :-
	the_constraint1_aux(X_I,X_J),
	the_constraint1(X_Is,X_J).

the_constraint1_aux(_,[]).
the_constraint1_aux(X_I,[X_J|X_Js]) :-
	the_constraint1_aux_aux(X_I,X_J),
	the_constraint1_aux(X_I,X_Js).

the_constraint1_aux_aux((X_I,I), (X_J,J)) :- !,
	(I // 9 =:= J // 9 , I =\= J ->
		write('\t'),
		write('I='), write(I), write(', '),
		write('J='), write(J), write(', '),
		nl,
		X_I #\= X_J
	;
		true
	).
the_constraint1_aux_aux(_,_).

the_constraint2([],_).
the_constraint2([X_I|X_Is],X_J) :-
	the_constraint2_aux(X_I,X_J),
	the_constraint2(X_Is,X_J).

the_constraint2_aux(_,[]).
the_constraint2_aux(X_I,[X_J|X_Js]) :-
	the_constraint2_aux_aux(X_I,X_J),
	the_constraint2_aux(X_I,X_Js).

the_constraint2_aux_aux((X_I,I), (X_J,J)) :- !,
	(I mod 9 =:= J mod 9 , I =\= J ->
		write('\t'),
		write('I='), write(I), write(', '),
		write('J='), write(J), write(', '),
		nl,
		X_I #\= X_J
	;
		true
	).
the_constraint2_aux_aux(_,_).

the_constraint3([],_).
the_constraint3([X_I|X_Is],X_J) :-
	the_constraint3_aux(X_I,X_J),
	the_constraint3(X_Is,X_J).

the_constraint3_aux(_,[]).
the_constraint3_aux(X_I,[X_J|X_Js]) :-
	the_constraint3_aux_aux(X_I,X_J),
	the_constraint3_aux(X_I,X_Js).

the_constraint3_aux_aux((X_I,I), (X_J,J)) :- !,
	((I mod 9)//3 =:= (J mod 9)//3 , I // 27 =:= J // 27 , I =\= J ->
		write('\t'),
		write('I='), write(I), write(', '),
		write('J='), write(J), write(', '),
		nl,
		X_I #\= X_J
	;
		true
	).
the_constraint3_aux_aux(_,_).

the_constraint4([],_,_,_,_).
the_constraint4([X_I|X_Is],X_J,X_H,X_Vars,X_Vars) :-
	the_constraint4_aux(X_I,X_J,X_H,X_Vars,X_Vars),
	the_constraint4(X_Is,X_J,X_H,X_Vars,X_Vars).

the_constraint4_aux(_,[],_,_,_).
the_constraint4_aux(X_I,[X_J|X_Js],X_H,X_Vars,X_Vars) :-
	the_constraint4_aux_aux(X_I,X_J,X_H,X_Vars,X_Vars),
	the_constraint4_aux(X_I,X_Js,X_H,X_Vars,X_Vars).

the_constraint4_aux_aux(_,_,[],_,_).
the_constraint4_aux_aux(X_I,X_J,[X_H|X_Hs],X_Vars,X_Vars) :-
	the_constraint4_aux_aux_aux(X_I,X_J,X_H,X_Vars,X_Vars),
	the_constraint4_aux_aux(X_I,X_J,X_Hs,X_Vars,X_Vars).

the_constraint4_aux_aux_aux((X_I,I), (X_J,J), (X_H,H), X_Vars, X_Vars) :- !,
	(Hp1 is H + 1, find_var(X_Vars,Hp1,X_Hp1), Hp2 is H + 2, find_var(X_Vars,Hp2,X_Hp2), I//9 =\= J//9 , J//9 =\= H//9 , I//9 =\=H//9 , I//27 =:= J//27 , J//27 =:= H//27 , ((I mod 9)//3 =\= (J mod 9)//3 , (J mod 9)//3 =\= (H mod 9)//3) , (I mod 9)//3 =\= (H mod 9)//3 , I < J , H mod 3 =:= 0 ->
		write('\t'),
		write('I='), write(I), write(', '),
		write('J='), write(J), write(', '),
		write('H='), write(H), write(', '),
		nl,
		X_I #= X_J #=> X_I#=X_H #\/ X_Hp1 #= X_I #\/ X_Hp2 #= X_I
	;
		true
	).
the_constraint4_aux_aux_aux(_,_,_,_,_).

the_constraint5([],_,_,_,_).
the_constraint5([X_I|X_Is],X_J,X_H,X_Vars,X_Vars) :-
	the_constraint5_aux(X_I,X_J,X_H,X_Vars,X_Vars),
	the_constraint5(X_Is,X_J,X_H,X_Vars,X_Vars).

the_constraint5_aux(_,[],_,_,_).
the_constraint5_aux(X_I,[X_J|X_Js],X_H,X_Vars,X_Vars) :-
	the_constraint5_aux_aux(X_I,X_J,X_H,X_Vars,X_Vars),
	the_constraint5_aux(X_I,X_Js,X_H,X_Vars,X_Vars).

the_constraint5_aux_aux(_,_,[],_,_).
the_constraint5_aux_aux(X_I,X_J,[X_H|X_Hs],X_Vars,X_Vars) :-
	the_constraint5_aux_aux_aux(X_I,X_J,X_H,X_Vars,X_Vars),
	the_constraint5_aux_aux(X_I,X_J,X_Hs,X_Vars,X_Vars).

the_constraint5_aux_aux_aux((X_I,I), (X_J,J), (X_H,H), X_Vars, X_Vars) :- !,
	(Hp9 is H + 9, find_var(X_Vars,Hp9,X_Hp9), Hp18 is H + 18, find_var(X_Vars,Hp18,X_Hp18), I mod 9 =\= J mod 9 , J mod 9 =\= H mod 9 , I mod 9 =\=H mod 9 , I//27 =\= J//27 , J//27 =\= H//27 , I//27 =\= H//27 , ((I mod 9)//3 =:= (J mod 9)//3 , (J mod 9)//3 =:= (H mod 9)//3) , I < J , (H//3) mod 9 =:= 0 ->
		write('\t'),
		write('I='), write(I), write(', '),
		write('J='), write(J), write(', '),
		write('H='), write(H), write(', '),
		nl,
		X_I #= X_J #=> X_I#=X_H #\/ X_Hp9 #= X_I #\/ X_Hp18 #= X_I
	;
		true
	).
the_constraint5_aux_aux_aux(_,_,_,_,_).

sudoku([]).
sudoku([X|Xs]) :-
	sudoku_constraint(X),
	sudoku(Xs).

sudoku_constraint((X,2)) :- !, X = 6.
sudoku_constraint((X,3)) :- !, X = 5.
sudoku_constraint((X,6)) :- !, X = 8.
sudoku_constraint((X,7)) :- !, X = 3.
sudoku_constraint((X,10)) :- !, X = 7.
sudoku_constraint((X,13)) :- !, X = 8.
sudoku_constraint((X,22)) :- !, X = 6.
sudoku_constraint((X,24)) :- !, X = 4.
sudoku_constraint((X,26)) :- !, X = 1.
sudoku_constraint((X,27)) :- !, X = 7.
sudoku_constraint((X,32)) :- !, X = 4.
sudoku_constraint((X,33)) :- !, X = 3.
sudoku_constraint((X,38)) :- !, X = 8.
sudoku_constraint((X,42)) :- !, X = 7.
sudoku_constraint((X,47)) :- !, X = 2.
sudoku_constraint((X,48)) :- !, X = 6.
sudoku_constraint((X,53)) :- !, X = 5.
sudoku_constraint((X,54)) :- !, X = 8.
sudoku_constraint((X,56)) :- !, X = 5.
sudoku_constraint((X,58)) :- !, X = 4.
sudoku_constraint((X,67)) :- !, X = 2.
sudoku_constraint((X,70)) :- !, X = 9.
sudoku_constraint((X,73)) :- !, X = 6.
sudoku_constraint((X,74)) :- !, X = 7.
sudoku_constraint((X,77)) :- !, X = 9.
sudoku_constraint((X,78)) :- !, X = 5.
sudoku_constraint((_,_)).

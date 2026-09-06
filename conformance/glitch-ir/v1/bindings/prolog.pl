:- initialization(main, main).

parse_line(Line, Key-Value) :-
    split_string(Line, "=", "", [Key, Value]).

value(Key, Pairs, Value) :-
    memberchk(Key-Value, Pairs).

requires_backtrace(Verified, Evidence, Source) :-
    (Verified = "PRESENT", Evidence \= "PRESENT")
    ;
    Source = "UNKNOWN".

main([Path]) :-
    read_file_to_string(Path, Text, []),
    split_string(Text, "\n", "\r", RawLines),
    exclude(=(""), RawLines, Lines),
    maplist(parse_line, Lines, Pairs),
    value("verification_label", Pairs, Verified),
    value("evidence", Pairs, Evidence),
    value("source", Pairs, Source),
    ( requires_backtrace(Verified, Evidence, Source) ->
        Verdict = "BACKTRACE", Operator = "GLT-0036", State = "CONTESTED"
    ;
        Verdict = "ACCEPT", Operator = "NONE", State = "ACCEPTED"
    ),
    value("vector_id", Pairs, Vector),
    value("protocol_version", Pairs, Version),
    format("~s|~s|~s|~s|~s~n", [Vector, Version, Verdict, Operator, State]).
main(_) :-
    throw(error(domain_error(arguments, 'usage: prolog.pl VECTOR'), _)).

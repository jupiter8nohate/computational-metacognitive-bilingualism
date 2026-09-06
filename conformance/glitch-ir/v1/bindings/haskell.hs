import System.Environment (getArgs)

parseKV :: String -> (String, String)
parseKV line =
    case break (== '=') line of
        (key, '=':value) -> (key, value)
        _ -> error ("invalid vector line: " ++ line)

require :: String -> [(String, String)] -> String
require key values =
    case lookup key values of
        Just value -> value
        Nothing -> error ("missing key: " ++ key)

main :: IO ()
main = do
    args <- getArgs
    case args of
        [path] -> do
            content <- readFile path
            let values = map parseKV . filter (not . null) $ lines content
                verified = require "verification_label" values
                evidence = require "evidence" values
                source = require "source" values
                backtrace = (verified == "PRESENT" && evidence /= "PRESENT") || source == "UNKNOWN"
                verdict = if backtrace then "BACKTRACE" else "ACCEPT"
                operator = if backtrace then "GLT-0036" else "NONE"
                state = if backtrace then "CONTESTED" else "ACCEPTED"
            putStrLn $ require "vector_id" values ++ "|" ++
                       require "protocol_version" values ++ "|" ++
                       verdict ++ "|" ++ operator ++ "|" ++ state
        _ -> error "usage: haskell.hs VECTOR"

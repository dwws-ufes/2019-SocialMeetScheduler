#!/usr/bin/env php
<?php

function scandirrecursive($target, $includeDirs=false, &$accumulator=null) {
    if($accumulator===null) $accumulator = [];
    if(is_dir($target)){
        if($includeDirs)
            $accumulator[] = $target;
        $files = glob("$target*", GLOB_MARK);
        foreach($files as $file)
            scandirrecursive($file, $includeDirs, $accumulator);
    } else
        $accumulator[] = $target;
    return $accumulator;
}

function similar_text_fn($first, $second){
    $float = 0.0;
    similar_text($first, $second, $float);
    return $float;
}

function contents_of($fn, $onNonExistent=null){
    if(is_file($fn))
        return file_get_contents($fn);
    else
        return $onNonExistent;
}

function split_lines($text){
    return preg_split('/\n|\r/',$text);
}

function count_lines($text){
    if($text===null || strlen($text)===0) return 0;
    return count(split_lines($text));
}

function sorted($arr){
    sort($arr);
    return $arr;
}

function chars_per_line(&$arr){
    $lines = $arr['lines'];
    $chars = $arr['chars'];
    $cpl = 0;
    if($lines>0)
        $cpl = $chars/$lines;
    $arr['chars_per_line'] = $cpl;
}

$files = array_merge(scandirrecursive('generated/'), scandirrecursive('final/'));
foreach($files as &$file) $file = substr($file, strpos($file, '/')+1);
unset($file);
$files = sorted(array_unique($files));

$summary = [];
foreach($files as $file){
    $summary[$file] = ['generated'=>[], 'final'=>[]];
    $generated = contents_of("generated/$file");
    $final = contents_of("final/$file");
    $summary[$file]['generated']['lines'] = count_lines($generated);
    $summary[$file]['generated']['chars'] = strlen($generated);
    $summary[$file]['final']['lines'] = count_lines($final);
    $summary[$file]['final']['chars'] = strlen($final);
    $summary[$file]['similarity'] = similar_text_fn($generated, $final);
    chars_per_line($summary[$file]['generated']);
    chars_per_line($summary[$file]['final']);
}

file_put_contents('summary.json', json_encode($summary, JSON_PRETTY_PRINT));

<?php
    $files = glob("descargas/*");
    $files = array_combine($files, array_map("filemtime", $files));
    arsort($files);
    $latest_file = key($files);
    #$nombre_imagen = $_POST[$latest_file];
    $json = array();
    $json['valor'] = $latest_file;
    echo json_encode($json);
?>
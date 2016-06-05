<?php

session_start();
unset($_SESSION['token']);
session_destroy();
header('location:../collaboration-login/');
?>
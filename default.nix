{ lib, fetchFromGitHub, buildPythonPackage, sleekxmpp, requests }:

buildPythonPackage rec {
  name = "phonectl-${version}";
  version = "git-20180305";

  src = fetchFromGitHub {
    owner  = "jb55";
    repo   = "phonectl";
    sha256 = "0k9bb305ldvmxmc7d88xjgapvcy39ryh4dwvaysp6401xjxrzgnw";
    rev    = "7fea40da5453b6c8607a2251817a394c517b27f9";
  };

  propagatedBuildInputs = [ sleekxmpp ];

  buildInputs = [ ];

  doCheck = false;

  meta = with lib; {
    description = "Python library for communicating with TREZOR Bitcoin Hardware Wallet";
    homepage = https://github.com/jb55/phonectl;
    license = licenses.mit;
    maintainers = with maintainers; [ jb55 ];
  };
}


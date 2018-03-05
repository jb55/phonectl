{ lib, fetchFromGitHub, buildPythonPackage, sleekxmpp, requests }:

buildPythonPackage rec {
  name = "phonectl-${version}";
  version = "git-20180305";

  src = ./.;

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


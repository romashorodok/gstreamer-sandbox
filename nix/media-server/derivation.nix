{ stdenv, pkgs, ... }:

stdenv.mkDerivation rec {
  name = "media-server-${version}";
  version = "0.0.1";

  src = ./.;

  buildInputs = with pkgs; [
    python311Full
    python311Packages.gst-python
    virtualenv
  ];

  buildPhase = ''
  '';

  installPhase = ''
    mkdir $out
  '';

  shellHook = ''
  '';
}

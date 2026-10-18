{
  description = "Flaker - Single-File Nix-Shell & Development Workspace Creator";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
  }: let
    systems = flake-utils.lib.defaultSystems;
  in
    flake-utils.lib.eachSystem systems (system: let
      pkgs = import nixpkgs {inherit system;};
      lib = pkgs.lib;

      runtimeLibs = with pkgs; [
        stdenv.cc.cc.lib
        zlib
        glib
        libxml2
        openssl
        libffi
      ];

      libsList = lib.concatStringsSep "," (
        map (p:
          if (p.pname or "") == "gcc"
          then "stdenv.cc.cc.lib"
          else (p.pname or p.name))
        runtimeLibs
      );

      flakerPackage = pkgs.python3Packages.buildPythonApplication {
        pname = "flaker";
        version = "0.3.0";
        src = ./.;
        pyproject = true;

        build-system = [
          pkgs.python3Packages.setuptools
        ];

        nativeBuildInputs = [
          pkgs.makeWrapper
        ];

        postFixup = ''
          wrapProgram $out/bin/flaker \
            --prefix PATH : ${lib.makeBinPath [pkgs.direnv]} \
            --set LIBS_LIST "${libsList}" \
            --set FLAKE_TEMPLATE "$out/${pkgs.python3.sitePackages}/flaker/flake.template" \
            --set FLAKER_ASSETS "$out/${pkgs.python3.sitePackages}/flaker/templates"

          # Prune compiled bytecode from template scaffolding directory
          find $out/${pkgs.python3.sitePackages}/flaker/templates -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
        '';

        doCheck = false;

        meta = with lib; {
          description = "Fast, modular Nix development environment and project scaffolding tool";
          homepage = "https://github.com/SpanishSyntax/Flaker";
          license = licenses.mit;
          mainProgram = "flaker";
        };
      };
    in {
      packages = {
        default = flakerPackage;
        flaker = flakerPackage;
      };

      apps = {
        default = {
          type = "app";
          program = "${flakerPackage}/bin/flaker";
        };
        flaker = {
          type = "app";
          program = "${flakerPackage}/bin/flaker";
        };
      };

      devShells.default = pkgs.mkShell {
        packages = with pkgs; [
          python3
          python3Packages.setuptools
          direnv
        ];
      };
    })
    // {
      overlays = {
        default = final: prev: {
          flaker = self.packages.${prev.stdenv.hostPlatform.system}.default;
        };
        flaker = self.overlays.default;
      };

      nixosModules = {
        default = self.nixosModules.flaker;
        flaker = {
          config,
          lib,
          pkgs,
          ...
        }: let
          cfg = config.programs.flaker;
          system = pkgs.stdenv.hostPlatform.system;
          defaultFlaker = self.packages.${system}.default;
        in {
          options.programs.flaker = {
            enable = lib.mkEnableOption "Flaker - Single-File Nix-Shell & Development Workspace Creator";

            package = lib.mkOption {
              type = lib.types.package;
              default = defaultFlaker;
              description = "The Flaker package to use.";
            };
          };

          config = lib.mkIf cfg.enable {
            environment.systemPackages = [cfg.package];
          };
        };
      };

      homeManagerModules = {
        default = self.homeManagerModules.flaker;
        flaker = {
          config,
          lib,
          pkgs,
          ...
        }: let
          cfg = config.programs.flaker;
          tomlFormat = pkgs.formats.toml {};
          system = pkgs.stdenv.hostPlatform.system;
          defaultFlaker = self.packages.${system}.default;
        in {
          options.programs.flaker = {
            enable = lib.mkEnableOption "Flaker - Single-File Nix-Shell & Development Workspace Creator";

            package = lib.mkOption {
              type = lib.types.package;
              default = defaultFlaker;
              description = "The Flaker package to use.";
            };

            settings = lib.mkOption {
              type = tomlFormat.type;
              default = {};
              description = "Custom roles and aliases written to ~/.config/flaker/roles.toml.";
            };
          };

          config = lib.mkIf cfg.enable {
            home.packages = [cfg.package];

            xdg.configFile."flaker/roles.toml" = lib.mkIf (cfg.settings != {}) {
              source = tomlFormat.generate "roles.toml" cfg.settings;
            };
          };
        };
      };
    };
}

{
  description = "Basecamp - Single-File Nix-Shell & Development Workspace Creator";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    prism = {
      url = "github:SpanishSyntax/Prism";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
    prism,
  }: let
    systems = flake-utils.lib.defaultSystems;
  in
    flake-utils.lib.eachSystem systems (system: let
      pkgs = import nixpkgs {
        inherit system;
        overlays = [prism.overlays.default];
      };
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

      basecampPackage = pkgs.python3Packages.buildPythonApplication {
        pname = "basecamp";
        version = "0.3.0";
        src = ./.;
        pyproject = true;

        build-system = [
          pkgs.python3Packages.setuptools
        ];

        propagatedBuildInputs = [
          pkgs.python3Packages.prism
        ];

        nativeBuildInputs = [
          pkgs.makeWrapper
        ];

        postFixup = ''
          wrapProgram $out/bin/basecamp \
            --prefix PATH : ${lib.makeBinPath [pkgs.direnv]} \
            --set LIBS_LIST "${libsList}" \
            --set FLAKE_TEMPLATE "$out/${pkgs.python3.sitePackages}/basecamp/flake.template" \
            --set BASECAMP_ASSETS "$out/${pkgs.python3.sitePackages}/basecamp/templates" \
            --set FLAKER_ASSETS "$out/${pkgs.python3.sitePackages}/basecamp/templates"

          # Prune compiled bytecode from template scaffolding directory
          find $out/${pkgs.python3.sitePackages}/basecamp/templates -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
        '';

        nativeCheckInputs = [
          pkgs.python3Packages.pytest
          pkgs.direnv
        ];

        checkPhase = ''
          runHook preCheck
          pytest
          runHook postCheck
        '';

        doCheck = true;

        meta = with lib; {
          description = "Fast, modular Nix development environment and project scaffolding tool";
          homepage = "https://github.com/SpanishSyntax/Basecamp";
          license = licenses.mit;
          mainProgram = "basecamp";
        };
      };
    in {
      packages = {
        default = basecampPackage;
        basecamp = basecampPackage;
        flaker = basecampPackage;
      };

      apps = {
        default = {
          type = "app";
          program = "${basecampPackage}/bin/basecamp";
        };
        basecamp = {
          type = "app";
          program = "${basecampPackage}/bin/basecamp";
        };
        flaker = {
          type = "app";
          program = "${basecampPackage}/bin/basecamp";
        };
      };

      devShells.default = pkgs.mkShell {
        packages = with pkgs; [
          python3
          python3Packages.setuptools
          python3Packages.pytest
          python3Packages.prism
          direnv
        ];
      };
    })
    // {
      overlays = {
        default = final: prev: {
          basecamp = self.packages.${prev.stdenv.hostPlatform.system}.default;
        };
        basecamp = self.overlays.default;
        flaker = self.overlays.default;
      };

      nixosModules = {
        default = self.nixosModules.basecamp;
        basecamp = {
          config,
          lib,
          pkgs,
          ...
        }: let
          cfg = config.programs.basecamp;
          system = pkgs.stdenv.hostPlatform.system;
          defaultBasecamp = self.packages.${system}.default;
        in {
          options.programs.basecamp = {
            enable = lib.mkEnableOption "Basecamp - Single-File Nix-Shell & Development Workspace Creator";

            package = lib.mkOption {
              type = lib.types.package;
              default = defaultBasecamp;
              description = "The Basecamp package to use.";
            };
          };

          config = lib.mkIf cfg.enable {
            environment.systemPackages = [cfg.package];
          };
        };
        flaker = self.nixosModules.basecamp;
      };

      homeManagerModules = {
        default = self.homeManagerModules.basecamp;
        basecamp = {
          config,
          lib,
          pkgs,
          ...
        }: let
          cfg = config.programs.basecamp;
          tomlFormat = pkgs.formats.toml {};
          system = pkgs.stdenv.hostPlatform.system;
          defaultBasecamp = self.packages.${system}.default;
        in {
          options.programs.basecamp = {
            enable = lib.mkEnableOption "Basecamp - Single-File Nix-Shell & Development Workspace Creator";

            package = lib.mkOption {
              type = lib.types.package;
              default = defaultBasecamp;
              description = "The Basecamp package to use.";
            };

            settings = lib.mkOption {
              type = tomlFormat.type;
              default = {};
              description = "Custom roles and aliases written to ~/.config/basecamp/roles.toml.";
            };
          };

          config = lib.mkIf cfg.enable {
            home.packages = [cfg.package];

            xdg.configFile."basecamp/roles.toml" = lib.mkIf (cfg.settings != {}) {
              source = tomlFormat.generate "roles.toml" cfg.settings;
            };
          };
        };
        flaker = self.homeManagerModules.basecamp;
      };
    };
}

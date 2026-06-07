[Español](README.es.md) | [English](README.en.md)

---

# AutoConfigOSCLI (v0.1.0)

**Automatizacion profesional de entornos para desarrolladores.**
*Primero offline. Reversible. IA hibrida.*

## Introduccion

AutoConfigOSCLI es una herramienta de linea de comandos para preparar, mantener y replicar entornos profesionales de desarrollo en Linux y macOS.

A diferencia de un gestor de dotfiles simple, aplica un enfoque completo:

- **Consciente del contexto**: adapta la instalacion al hardware, tipo de maquina y rol del usuario.
- **Perfiles por niveles**: `Lite`, `Mid` y `Full` para evitar instalar mas de lo necesario.
- **Seguro y reversible**: registra cambios y ofrece auditoria, copias de seguridad y degradacion.
- **Gestion remota sin agentes**: configura servidores por SSH sin instalar servicios persistentes.

## Principios

1. **Primero offline**: la resolucion de perfiles y la validacion funcionan sin internet.
2. **Reversible**: el estado se guarda localmente y permite volver atras.
3. **Idempotente**: repetir el mismo comando no deberia romper el sistema.
4. **IA transparente**: la IA recomienda y explica, pero no ejecuta sin confirmacion.
5. **Sin agentes**: usa SSH y configuracion nativa del sistema.

## Instalacion

```bash
git clone https://github.com/yourusername/AutoConfigOSCLI.git
cd AutoConfigOSCLI
./init.sh
```

`init.sh` comprueba Python 3, crea un entorno virtual, instala dependencias y registra el comando `autoconfigoscli`.

No instala paquetes del sistema ni modifica archivos raiz durante la instalacion inicial.

## Uso basico seguro

Explora sin aplicar cambios con `--dry-run`.

```bash
autoconfigoscli profiles list
autoconfigoscli profiles show backend-python-dev-postgresql-mid
autoconfigoscli install backend-python-dev-postgresql-mid --dry-run --verbose
```

## Perfiles y niveles

| Nivel | Enfoque | Herramientas tipicas | Editores |
|:---|:---|:---|:---|
| **Lite** | CLI, eficiencia, pocos recursos | TUI, clientes CLI | `micro`, `neovim` |
| **Mid** | Flujo estandar | Docker, runtimes | `vscode` |
| **Full** | Productividad completa | Bases de datos GUI, IDEs | JetBrains, DBeaver |

## Casos de uso

- Preparar una estacion de trabajo nueva.
- Replicar un entorno entre maquinas.
- Auditar cambios de configuracion.
- Simular instalaciones antes de aplicarlas.
- Gestionar perfiles para backend, frontend, bases de datos o servidores.

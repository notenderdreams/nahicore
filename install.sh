#!/usr/bin/env bash
set -euo pipefail

PLUGIN_NAME="nahicore"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="${SCRIPT_DIR}"

TARGET_SCOPE="global"
USE_SYMLINK=false
UNINSTALL=false

show_help() {
  cat <<EOF
nahicore - Personal Agent Skills & Tooling Suite Installer

Usage:
  ./install.sh [options]

Options:
  -g, --global      Install globally to ~/.gemini/config/plugins/ and ~/.agents/skills/ (default)
  -p, --project     Install skills locally to ./.agents/skills/ (project scope)
  -s, --symlink     Create symbolic links instead of copying files (recommended for development)
  -u, --uninstall   Uninstall nahicore and its member skills from target locations
  -h, --help        Show this help message

Examples:
  ./install.sh                  # Copy nahicore plugin and skills to global locations
  ./install.sh --symlink        # Symlink to global locations (dev mode)
  ./install.sh --project        # Install member skills into current project's .agents/
  ./install.sh --uninstall      # Remove installations
EOF
}

# Parse flags
while [[ $# -gt 0 ]]; do
  case "$1" in
    -g|--global)
      TARGET_SCOPE="global"
      shift
      ;;
    -p|--project)
      TARGET_SCOPE="project"
      shift
      ;;
    -s|--symlink)
      USE_SYMLINK=true
      shift
      ;;
    -u|--uninstall)
      UNINSTALL=true
      shift
      ;;
    -h|--help)
      show_help
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      show_help
      exit 1
      ;;
  esac
done

install_plugin() {
  local plugins_dir="$1"
  local dest="${plugins_dir}/${PLUGIN_NAME}"

  if [[ "${UNINSTALL}" == true ]]; then
    if [[ -d "${dest}" || -L "${dest}" ]]; then
      rm -rf "${dest}"
      echo "✓ Removed plugin ${dest}"
    fi
    return
  fi

  mkdir -p "${plugins_dir}"
  if [[ -e "${dest}" || -L "${dest}" ]]; then
    rm -rf "${dest}"
  fi

  if [[ "${USE_SYMLINK}" == true ]]; then
    ln -s "${SOURCE_DIR}" "${dest}"
    echo "✓ Symlinked plugin -> ${dest}"
  else
    mkdir -p "${dest}"
    cp -R "${SOURCE_DIR}/"* "${dest}/"
    echo "✓ Installed plugin -> ${dest}"
  fi
}

install_member_skills() {
  local target_skills_dir="$1"

  if [[ ! -d "${SOURCE_DIR}/skills" ]]; then
    return
  fi

  mkdir -p "${target_skills_dir}"

  for skill_dir in "${SOURCE_DIR}/skills"/*; do
    if [[ ! -d "${skill_dir}" ]]; then
      continue
    fi

    local skill_name
    skill_name="$(basename "${skill_dir}")"
    local dest="${target_skills_dir}/${skill_name}"

    if [[ "${UNINSTALL}" == true ]]; then
      if [[ -d "${dest}" || -L "${dest}" ]]; then
        rm -rf "${dest}"
        echo "✓ Removed skill ${dest}"
      fi
      continue
    fi

    if [[ -e "${dest}" || -L "${dest}" ]]; then
      rm -rf "${dest}"
    fi

    if [[ "${USE_SYMLINK}" == true ]]; then
      ln -s "${skill_dir}" "${dest}"
      echo "✓ Symlinked skill [${skill_name}] -> ${dest}"
    else
      mkdir -p "${dest}"
      cp -R "${skill_dir}/"* "${dest}/"
      echo "✓ Installed skill [${skill_name}] -> ${dest}"
    fi
  done
}

if [[ "${TARGET_SCOPE}" == "global" ]]; then
  # 1. Antigravity plugin directory (discovers nahicore and all skills in skills/*)
  install_plugin "${HOME}/.gemini/config/plugins"
  # 2. Universal agent skills directory (Zed, Claude Code, etc.)
  install_member_skills "${HOME}/.agents/skills"
else
  # Project-local directory
  install_member_skills "./.agents/skills"
fi

if [[ "${UNINSTALL}" != true ]]; then
  echo ""
  echo "nahicore is ready! Skills (including liquid-metal) are available across agent sessions."
fi

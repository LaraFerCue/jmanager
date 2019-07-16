from pathlib import PosixPath
from typing import List, Callable

from jmanager.models.distribution import Distribution, Component, Version, Architecture
from jmanager.models.jail import JailError
from jmanager.utils.file_utils import remove_immutable_path, extract_tarball_into
from src.factories.data_set_factory import DataSetFactory


class BaseJailFactory:
    SNAPSHOT_NAME = "jmanager_base_jail"

    def __init__(self, jail_root_path: PosixPath, data_set_factory: DataSetFactory):
        self._jail_root_path = jail_root_path
        self._data_set_factory = data_set_factory

        if jail_root_path.exists() and not jail_root_path.is_dir():
            raise PermissionError("The jail root path exists and it is not a directory")
        elif not jail_root_path.exists():
            jail_root_path.mkdir(parents=True)

    @property
    def data_set_factory(self) -> DataSetFactory:
        return self._data_set_factory

    def get_jail_mountpoint(self, jail_data_set_name: str) -> PosixPath:
        jail_path = self._jail_root_path.joinpath(jail_data_set_name)
        return jail_path

    @staticmethod
    def get_data_set_name(distribution) -> str:
        return f"{distribution.version}_{distribution.architecture.value}"

    def get_snapshot_name(self, component_list: List[Component]):
        components = component_list.copy()
        if Component.BASE in components:
            components.remove(Component.BASE)

        components.sort()
        if not components:
            return self.SNAPSHOT_NAME
        component_extension = '_'.join([dist.value for dist in components])
        return f"{self.SNAPSHOT_NAME}_{component_extension}"

    def base_jail_exists(self, distribution: Distribution):
        base_jail_name = self.get_data_set_name(distribution)
        snapshot_name = self.get_snapshot_name(component_list=distribution.components)
        return self._data_set_factory.snapshot_exists(base_jail_name, snapshot_name)

    def create_base_jail(self, distribution: Distribution, path_to_tarballs: PosixPath,
                         callback: Callable[[str, int, int], None] = None):
        if self.base_jail_exists(distribution):
            raise JailError(f"The base jail for '{distribution.version}/{distribution.architecture.value}' exists")

        for component in distribution.components:
            if not path_to_tarballs.joinpath(f"{component.value}.txz").is_file():
                raise FileNotFoundError(f"Component '{component.value}' not found in {path_to_tarballs}")

        jail_data_set_name = f"{distribution.version}_{distribution.architecture.value}"
        jail_path = self.get_jail_mountpoint(jail_data_set_name=jail_data_set_name)
        if not self._data_set_factory.base_data_set_exists(data_set_name=self.get_data_set_name(distribution)):
            self._data_set_factory.create_base_data_set(self.get_data_set_name(distribution), jail_path)
        else:
            remove_immutable_path(jail_path)

        self.extract_components_into_base_jail(components=distribution.components,
                                               jail_path=jail_path,
                                               path_to_tarballs=path_to_tarballs,
                                               data_set_name=self.get_data_set_name(distribution=distribution),
                                               callback=callback)

    def extract_components_into_base_jail(self, components: List[Component], jail_path: PosixPath,
                                          path_to_tarballs: PosixPath, data_set_name: str,
                                          callback: Callable[[str, int, int], None]):
        processed_components = []
        for component in components:
            extract_tarball_into(
                jail_path=jail_path,
                path_to_tarball=path_to_tarballs.joinpath(f"{component.value}.txz"),
                callback=callback
            )
            processed_components.append(component)
            snapshot_name = self.get_snapshot_name(component_list=processed_components)

            if not self._data_set_factory.snapshot_exists(data_set_name=data_set_name, snapshot=snapshot_name):
                self._data_set_factory.create_snapshot(data_set_name=data_set_name, snapshot=snapshot_name)

    def destroy_base_jail(self, distribution: Distribution):
        base_jail_data_set_name = self.get_data_set_name(distribution)
        if self.base_jail_exists(distribution=distribution):
            snapshot_name = self.get_snapshot_name(component_list=distribution.components)
            self._data_set_factory.delete_snapshot(data_set_name=base_jail_data_set_name,
                                                   snapshot_name=snapshot_name)

        if not len(self.list_base_jails()):
            self._data_set_factory.delete_data_set(data_set_name=f"{base_jail_data_set_name}")

    def list_base_jails(self) -> List[Distribution]:
        distribution_list = []
        for snapshot in self._data_set_factory.list_of_snapshots():
            snapshot_name = snapshot.split('@')[1].replace(f"{self.SNAPSHOT_NAME}", '')
            data_set = snapshot.split('@')[0].replace(f"{self._data_set_factory}/", '')

            components = []
            for component in snapshot_name.split('_'):
                if component:
                    components.append(Component(component))
            version = Version.from_string(data_set.split('_')[0])
            architecture = Architecture(data_set.split('_')[1])
            distribution_list.append(Distribution(version=version, architecture=architecture,
                                                  components=components))
        return distribution_list

    def __eq__(self, other: 'BaseJailFactory') -> bool:
        return self._data_set_factory == other._data_set_factory and self._jail_root_path == other._jail_root_path

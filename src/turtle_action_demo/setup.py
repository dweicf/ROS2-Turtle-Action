from setuptools import find_packages, setup

package_name = 'turtle_action_demo'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch',
            ['launch/turtle_action.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='dwei',
    maintainer_email='dweicf@163.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
             'action_server = turtle_action_demo.action_server:main',
             'action_client = turtle_action_demo.action_client:main',
        ],
    },
)

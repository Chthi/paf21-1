FROM ros:noetic

# set up the default shell used by RUN tags
SHELL ["/bin/bash", "-c"]

# install pip
RUN apt-get update && apt-get install -y python3-pip \
    && rm -rf /var/lib/apt/lists/*

# alias python3 as python
RUN apt-get update && apt-get install -y python-is-python3 \
    && rm -rf /var/lib/apt/lists/*

# install ros-related dependencies (mainly for messaging)
RUN apt-get update && apt-get install -y \
        ros-noetic-cv-bridge ros-noetic-vision-opencv \
        ros-noetic-ackermann-msgs \
    && rm -rf /var/lib/apt/lists/*

# install pip dependencies
RUN python -m pip install pip --upgrade
ADD ./requirements.txt /app/requirements.txt
RUN python -m pip install -r /app/requirements.txt

# test + lint the source code
ADD ./node /app/src/perception
WORKDIR /app/src/perception/src
RUN source /opt/ros/noetic/setup.bash && \
    python -m pytest tests && \
    pylint perception --fail-under=9.5 --extension-pkg-whitelist=cv2

# deploy the source code to ROS using catkin
WORKDIR /app/catkin_ws/src
RUN source /opt/ros/noetic/setup.bash && catkin_init_workspace && ln -s /app/src .
WORKDIR /app/catkin_ws
RUN source /opt/ros/noetic/setup.bash && catkin_make

# register a startup procedure to launch the ROS node
ADD ./ros_entrypoint.sh /ros_entrypoint.sh
ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["perception", "perception.launch", "--wait"]

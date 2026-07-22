FROM ubuntu:22.04
RUN apt-get update && DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get -y install tzdata curl wget mc
RUN apt-get update && \
    apt-get install -y software-properties-common curl

RUN apt-get install -y apt-transport-https ca-certificates build-essential libpq-dev libssl-dev openssl libffi-dev zlib1g-dev curl unzip libgconf-2-4

# install node.js
RUN apt-get update && apt-get install -y ca-certificates curl gnupg
RUN curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg
ENV NODE_MAJOR=22
RUN echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list
RUN apt-get update && apt-get install nodejs -y

# Install the locales package
RUN apt-get update && apt-get install -y locales

# Uncomment or generate the Russian locale
RUN sed -i '-e s/# ru_RU.UTF-8 UTF-8/ru_RU.UTF-8 UTF-8/' /etc/locale.gen && locale-gen

# Set environment variables for the system
ENV LANG=ru_RU.UTF-8
ENV LANGUAGE=ru_RU:ru
ENV LC_ALL=ru_RU.UTF-8

#install PHP
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    dpkg -l | grep php | tee packages.txt && \
    add-apt-repository -y ppa:ondrej/php
RUN apt-get update && \
    apt-get install -y php8.2 && \
    apt-get install -y php8.2-cli && \
    apt-get install -y php8.2-curl && \
    apt-get install -y php8.2-pdo && \
    apt-get install -y php8.2-pgsql
RUN apt-get install -y php8.2-dom && \
    apt-get install -y php8.2-imagick && \
    apt-get install -y php8.2-mbstring && \
    apt-get install -y php8.2-zip && \
    apt-get install -y php8.2-gd && \
    apt-get install -y php8.2-intl

#Install composer
RUN php -r "copy('https://getcomposer.org/installer', 'composer-setup.php');" && \
php composer-setup.php --install-dir=/usr/local/bin --filename=composer && \
php -r "unlink('composer-setup.php');" && \
chmod a+x /usr/local/bin/composer

# Create the user
ARG user_id
ARG group_id
ARG user

RUN groupadd --gid $group_id $user \
    && useradd --uid $user_id --gid $group_id -m $user \
    #
    # [Optional] Add sudo support. Omit if you don't need to install software after connecting.
    && apt-get update \
    && apt-get install -y sudo \
    && echo $user ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$user \
    && chmod 0440 /etc/sudoers.d/$user


WORKDIR /chebupelka
COPY ./chebupelka/* .
ENV PATH="/chebupelka:$PATH"

USER ${user}

#install uv
# Download the latest installer
ADD https://astral.sh/uv/install.sh /home/${user}/uv-installer.sh

# Run the installer then remove it
RUN ls -la /home/${user} && sudo chown ${user}:${user} /home/${user}/uv-installer.sh && sh /home/${user}/uv-installer.sh
RUN rm /home/${user}/uv-installer.sh

# Ensure the installed binary is on the `PATH`
ENV PATH="/home/${user}/.local/bin/:$PATH"

RUN uv python install 3.12.2






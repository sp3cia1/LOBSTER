#include <sys/socket.h>
#include <stdio.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <iostream>

int main()
{
    int socket_fd = socket(AF_INET, SOCK_STREAM, 0);
    // AF_INET -> ipv4, SOCK_STREAM ->TCP, 0->pick the default protocol for these 2
    if (socket_fd == -1)
    {
        perror("socket");
        return 1;
    }
    int opt = 1;
    //setsocketopt -> set socket options, so_reuseaddr -> after disconnection this port instantly becomes availaible instead of 60 seconds wait.
    if (setsockopt(socket_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) == -1) {
        perror("setsockopt");
        close(socket_fd);
        return 1;
    }
    sockaddr_in server_addr;
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(54321); // htons -> host to network short
    server_addr.sin_addr.s_addr = INADDR_ANY;
    // INADDR_ANY -> accept connection on thsi port from anywhwere.

    if (bind(socket_fd, reinterpret_cast<sockaddr *>(&server_addr), sizeof(server_addr)) == -1)
    {
        // casting our sockaddr_in(ipv4) as the generic sockaddr used by linux kernel to handle many types of addresses.
        perror("bind");
        close(socket_fd);
        return -1;
    }

    if (listen(socket_fd, 5) == -1)
    {
        // 5 is the backlog of how many connections can wait in line
        perror("listen");
        close(socket_fd);
        return -1;
    }

    std::cout << "Listening on port 54321 ...\n";
    sockaddr_in client_addr;

    while (true)
    {
        socklen_t client_addr_len = sizeof(client_addr);
        int client_fd = accept(socket_fd, reinterpret_cast<sockaddr *>(&client_addr), &client_addr_len);
        // accept is read-write so it wants a pointer we cant directly pass sizeof like we did for bind as that was read only
        if (client_fd == -1)
        {
            perror("accept");
            continue;
        }
        const size_t MAX_LINE = 1024;
        std::string buffer;
        while(true){
            char temp[512];
            ssize_t bytesRead = read(client_fd, temp,sizeof(temp));
            if (bytesRead <= 0) break;
            buffer.append(temp, bytesRead);
            if (buffer.size() > MAX_LINE){
                std::cerr << "Line too long, closing connection\n";
                break;
            }
            size_t pos;
            while((pos = buffer.find('\n')) != std::string::npos){
                std::string message = buffer.substr(0,pos);
                buffer.erase(0,pos+1);
                std::cout << "Message: " << message << "\n";
            }
        }
        close(client_fd);
    }
    close(socket_fd);
}
package org.example.upgradeprobe;

import java.io.IOException;
import jakarta.servlet.Filter;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.ServletRequest;
import jakarta.servlet.ServletResponse;

/** Extension built for Tomcat 10 and later (jakarta.servlet). */
public class ProbeFilter implements Filter {
    public ProbeFilter() {
        System.out.println("UPGRADE-PROBE loaded: jakarta variant");
    }

    @Override
    public void doFilter(ServletRequest req, ServletResponse res, FilterChain chain) throws IOException, ServletException {
        chain.doFilter(req, res);
    }
}

package org.example.upgradeprobe;

import java.io.IOException;
import javax.servlet.Filter;
import javax.servlet.FilterChain;
import javax.servlet.ServletException;
import javax.servlet.ServletRequest;
import javax.servlet.ServletResponse;

/** Extension built for Tomcat 9 and earlier (javax.servlet). */
public class ProbeFilter implements Filter {
    public ProbeFilter() {
        System.out.println("UPGRADE-PROBE loaded: javax variant");
    }

    @Override
    public void doFilter(ServletRequest req, ServletResponse res, FilterChain chain) throws IOException, ServletException {
        chain.doFilter(req, res);
    }
}
